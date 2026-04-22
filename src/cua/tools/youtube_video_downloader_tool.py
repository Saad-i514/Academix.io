import os
import subprocess
import time
import glob
import threading
import random
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Type, Optional, List, Dict, Callable, Any
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import yt_dlp
from faster_whisper import WhisperModel

# Setup logging
logger = logging.getLogger("Academix.YouTubeBypass")

# Global Whisper Model (Thread-safe for inference)
MODEL = WhisperModel("base", device="cpu", compute_type="int8")

# ============================================================================
# Bot Bypass Components
# ============================================================================

class ErrorType(Enum):
    """Classification of errors for appropriate handling"""
    BOT_DETECTION = "bot_detection"
    NETWORK_ERROR = "network"
    INVALID_URL = "invalid_url"
    COOKIE_AUTH_FAILED = "cookie_auth_failed"
    EXTRACTION_FAILED = "extraction_failed"
    UNKNOWN = "unknown"

# Patterns that indicate bot detection
BOT_DETECTION_PATTERNS = [
    "Sign in to confirm you're not a bot",
    "HTTP Error 429",
    "Too Many Requests",
    "bot detection",
    "captcha",
    "unusual traffic",
]

# User-friendly error messages
ERROR_MESSAGES = {
    ErrorType.BOT_DETECTION: (
        "YouTube detected automated access. The system attempted {attempts} times "
        "with different configurations. To resolve this:\n"
        "1. Wait a few minutes and try again\n"
        "2. Provide YouTube cookies via YOUTUBE_COOKIE_PATH environment variable\n"
        "3. Contact support if the issue persists"
    ),
    ErrorType.INVALID_URL: (
        "The YouTube URL is invalid or the video is not accessible. "
        "Please check:\n"
        "1. The URL is correct and complete\n"
        "2. The video is public and not deleted\n"
        "3. You have permission to access the video"
    ),
    ErrorType.COOKIE_AUTH_FAILED: (
        "Cookie authentication failed. Please ensure:\n"
        "1. Cookies are in Netscape format\n"
        "2. Cookies are from a recent YouTube session\n"
        "3. The cookie file path is correct: {cookie_path}\n"
        "To export cookies, use a browser extension like 'Get cookies.txt'"
    ),
    ErrorType.NETWORK_ERROR: (
        "Network error occurred while accessing YouTube. "
        "This may be temporary. Please try again in a few moments."
    ),
    ErrorType.EXTRACTION_FAILED: (
        "Failed to extract video information after trying multiple methods. "
        "This may indicate YouTube has changed their API. Please report this issue."
    ),
}

@dataclass
class BotBypassConfig:
    """Configuration for bot bypass mechanisms"""
    user_agents: List[str]
    cookie_path: Optional[str]
    max_retries: int
    base_delay: float
    max_delay: float
    enable_logging: bool
    
    @classmethod
    def from_env(cls) -> 'BotBypassConfig':
        """Load configuration from environment variables with defaults"""
        # Default user agent pool
        default_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        
        # Load from environment or use defaults
        user_agents_str = os.environ.get("YOUTUBE_USER_AGENTS", "")
        user_agents = [ua.strip() for ua in user_agents_str.split(",")] if user_agents_str else default_user_agents
        
        cookie_path = os.environ.get("YOUTUBE_COOKIE_PATH")
        max_retries = int(os.environ.get("YOUTUBE_MAX_RETRIES", "4"))
        base_delay = float(os.environ.get("YOUTUBE_BASE_DELAY", "2.0"))
        max_delay = float(os.environ.get("YOUTUBE_MAX_DELAY", "32.0"))
        enable_logging = os.environ.get("YOUTUBE_ENABLE_LOGGING", "true").lower() == "true"
        
        return cls(
            user_agents=user_agents,
            cookie_path=cookie_path,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            enable_logging=enable_logging,
        )
    
    def validate(self) -> List[str]:
        """Validate configuration and return warnings"""
        warnings = []
        
        if len(self.user_agents) < 3:
            warnings.append("User agent pool has fewer than 3 agents, may be less effective")
        
        if self.max_retries < 1:
            warnings.append("max_retries is less than 1, retries disabled")
        
        if self.base_delay < 0.5:
            warnings.append("base_delay is very low, may trigger rate limits")
        
        if self.cookie_path and not os.path.exists(self.cookie_path):
            warnings.append(f"Cookie file not found: {self.cookie_path}")
        
        return warnings


class UserAgentRotator:
    """Manages pool of realistic user agents and provides rotation"""
    
    def __init__(self, user_agents: List[str]):
        self.user_agents = user_agents
        self._last_agent = None
    
    def get_random_user_agent(self) -> str:
        """Returns a randomly selected user agent from the pool"""
        return random.choice(self.user_agents)
    
    def get_different_user_agent(self, previous: str) -> str:
        """Returns a user agent different from the previous one"""
        available = [ua for ua in self.user_agents if ua != previous]
        if not available:
            return self.get_random_user_agent()
        return random.choice(available)


class CookieManager:
    """Handles cookie loading and validation"""
    
    def __init__(self, cookie_path: Optional[str] = None):
        self.cookie_path = cookie_path
    
    def has_cookies(self) -> bool:
        """Returns True if cookies are configured"""
        return self.cookie_path is not None and os.path.exists(self.cookie_path)
    
    def get_cookie_path(self) -> Optional[str]:
        """Returns path to cookie file if available"""
        return self.cookie_path if self.has_cookies() else None
    
    def validate_cookies(self) -> bool:
        """Validates cookie file format and existence"""
        if not self.cookie_path:
            return True  # No cookies is valid
        
        if not os.path.exists(self.cookie_path):
            return False
        
        # Basic validation: check if file is readable
        try:
            with open(self.cookie_path, 'r') as f:
                f.read(100)  # Read first 100 bytes
            return True
        except Exception:
            return False


class ExtractionStrategyManager:
    """Manages fallback extraction methods"""
    
    def get_extractor_args(self) -> dict:
        """Returns yt-dlp extractor arguments with fallback strategies"""
        return {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash'],
            }
        }
    
    def log_successful_strategy(self, info: dict) -> None:
        """Logs which extraction method succeeded"""
        extractor = info.get('extractor', 'unknown')
        logger.info(f"Extraction successful using method: {extractor}")


class RetryHandler:
    """Implements exponential backoff retry logic"""
    
    def __init__(self, max_retries: int = 4, base_delay: float = 2.0, max_delay: float = 32.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def get_delay(self, attempt: int) -> float:
        """Calculates delay for given attempt number"""
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)
    
    def execute_with_retry(
        self, 
        func: Callable, 
        bypass_manager: 'BotBypassManager',
        *args, 
        **kwargs
    ) -> Any:
        """Executes function with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Update yt-dlp options for this attempt
                if 'ydl_opts' in kwargs:
                    kwargs['ydl_opts'] = bypass_manager.get_ydl_options(attempt)
                
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Retry successful on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries and bypass_manager.should_retry(e):
                    delay = self.get_delay(attempt)
                    logger.warning(
                        f"YouTube download failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {delay}s: {str(e)}"
                    )
                    time.sleep(delay)
                else:
                    break
        
        # All retries exhausted
        raise last_error


def classify_error(error: Exception) -> ErrorType:
    """Classifies error type for appropriate handling"""
    error_str = str(error).lower()
    
    # Check for bot detection patterns
    for pattern in BOT_DETECTION_PATTERNS:
        if pattern.lower() in error_str:
            return ErrorType.BOT_DETECTION
    
    # Check for network errors
    if any(term in error_str for term in ["connection", "timeout", "network", "dns"]):
        return ErrorType.NETWORK_ERROR
    
    # Check for invalid URL
    if any(term in error_str for term in ["invalid", "not found", "unavailable", "private"]):
        return ErrorType.INVALID_URL
    
    # Check for cookie auth failures
    if "cookie" in error_str:
        return ErrorType.COOKIE_AUTH_FAILED
    
    # Check for extraction failures
    if "extract" in error_str:
        return ErrorType.EXTRACTION_FAILED
    
    return ErrorType.UNKNOWN


class BotBypassManager:
    """Orchestrates all bot bypass mechanisms"""
    
    def __init__(self, config: BotBypassConfig):
        self.config = config
        self.user_agent_rotator = UserAgentRotator(config.user_agents)
        self.cookie_manager = CookieManager(config.cookie_path)
        self.extraction_manager = ExtractionStrategyManager()
        self.retry_handler = RetryHandler(
            max_retries=config.max_retries,
            base_delay=config.base_delay,
            max_delay=config.max_delay,
        )
        self._current_user_agent = None
        
        # Validate configuration
        warnings = config.validate()
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")
    
    def get_ydl_options(self, attempt: int = 0) -> dict:
        """Returns yt-dlp options dict with bypass mechanisms applied"""
        # Select user agent (different one for retries)
        if attempt == 0 or self._current_user_agent is None:
            self._current_user_agent = self.user_agent_rotator.get_random_user_agent()
        else:
            self._current_user_agent = self.user_agent_rotator.get_different_user_agent(
                self._current_user_agent
            )
        
        # Build yt-dlp options with more flexible format selection
        options = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best[height<=720]/best',
            'quiet': not self.config.enable_logging,
            'no_warnings': not self.config.enable_logging,
            'user_agent': self._current_user_agent,
            'extractor_args': self.extraction_manager.get_extractor_args(),
        }
        
        # Add cookies if available
        if self.cookie_manager.has_cookies():
            options['cookiefile'] = self.cookie_manager.get_cookie_path()
        
        if self.config.enable_logging:
            logger.info(f"Using user agent: {self._current_user_agent[:50]}...")
        
        return options
    
    def should_retry(self, error: Exception) -> bool:
        """Determines if an error is retryable"""
        error_type = classify_error(error)
        
        # Retry bot detection and network errors
        return error_type in [ErrorType.BOT_DETECTION, ErrorType.NETWORK_ERROR]
    
    def get_user_friendly_error(self, error: Exception, attempts: int = 1) -> str:
        """Converts technical errors to user-friendly messages"""
        error_type = classify_error(error)
        
        template = ERROR_MESSAGES.get(error_type, "An unexpected error occurred: {error}")
        
        # Format message with context
        if error_type == ErrorType.BOT_DETECTION:
            return template.format(attempts=attempts)
        elif error_type == ErrorType.COOKIE_AUTH_FAILED:
            return template.format(cookie_path=self.config.cookie_path or "not configured")
        else:
            return template.format(error=str(error))


# ============================================================================
# Streaming Transcription Manager (Enhanced with Bot Bypass)
# ============================================================================

class MultimediaProcessorInput(BaseModel):
    youtube_url: Optional[str] = Field(None, description="YouTube video URL")
    media_path: Optional[str] = Field(None, description="Path to a local audio or video file")

class StreamingTranscriptionManager:
    """Manages the real-time pipe from yt-dlp/file to ffmpeg chunks to faster-whisper."""
    
    def __init__(self, segment_time: int = 30, bypass_manager: Optional['BotBypassManager'] = None):
        self.segment_time = segment_time
        self.chunk_dir = Path("transcription_chunks")
        self.chunk_dir.mkdir(exist_ok=True)
        self.results: Dict[int, str] = {}
        self.active_workers = 0
        self.lock = threading.Lock()
        self.is_ffmpeg_done = False
        self.bypass_manager = bypass_manager

    def transcribe_chunk(self, chunk_file: str, index: int):
        """Worker function for a single chunk."""
        try:
            segments, _ = MODEL.transcribe(chunk_file)
            text = "".join([s.text for s in segments])
            with self.lock:
                self.results[index] = text
        except Exception as e:
            with self.lock:
                self.results[index] = f"[Error transcribing chunk {index}: {str(e)}]"
        finally:
            with self.lock:
                self.active_workers -= 1

    def monitor_chunks(self, executor: ThreadPoolExecutor):
        """Thread that watches for new finished chunks from ffmpeg."""
        processed_indices = set()
        
        while not self.is_ffmpeg_done or len(processed_indices) < self._count_finished_chunks():
            # Find all wav files except the one currently being written (highest index likely)
            chunks = sorted(glob.glob(str(self.chunk_dir / "chunk_*.wav")))
            
            # If ffmpeg is still running, avoid the last chunk because it might be incomplete
            to_process = chunks[:-1] if not self.is_ffmpeg_done else chunks
            
            for chunk_path in to_process:
                try:
                    index = int(Path(chunk_path).stem.split('_')[1])
                    if index not in processed_indices:
                        with self.lock:
                            self.active_workers += 1
                        executor.submit(self.transcribe_chunk, chunk_path, index)
                        processed_indices.add(index)
                except (ValueError, IndexError):
                    continue
            
            time.sleep(1) # Wait for more chunks

    def _count_finished_chunks(self) -> int:
        return len(glob.glob(str(self.chunk_dir / "chunk_*.wav")))
    
    def _extract_youtube_audio_url(self, source: str, ydl_opts: dict) -> str:
        """Extract audio URL from YouTube video with retry logic and fallback strategies"""
        if self.bypass_manager:
            # Use retry handler with enhanced fallback
            def extract_with_opts(ydl_opts):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(source, download=False)
                    self.bypass_manager.extraction_manager.log_successful_strategy(info)
                    return info['url']
            
            try:
                return self.bypass_manager.retry_handler.execute_with_retry(
                    extract_with_opts,
                    self.bypass_manager,
                    ydl_opts=ydl_opts
                )
            except Exception as e:
                error_str = str(e)
                # If bot detection fails, try alternative extraction methods
                if "Sign in to confirm you're not a bot" in error_str:
                    logger.warning("Bot detection triggered, trying alternative extraction methods...")
                    return self._try_alternative_extraction(source)
                # If format not available, try alternative formats
                elif "Requested format is not available" in error_str or "format" in error_str.lower():
                    logger.warning("Format not available, trying alternative formats...")
                    return self._try_alternative_extraction(source)
                raise e
        else:
            # Fallback to simple extraction
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source, download=False)
                return info['url']
    
    def _try_alternative_extraction(self, source: str) -> str:
        """Try alternative extraction methods when bot detection occurs"""
        alternative_configs = [
            # Try with more flexible format selection for production
            {
                'format': 'worst[ext=m4a]/worst[ext=mp3]/worstaudio/worst',
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                        'skip': ['hls'],
                    }
                }
            },
            # Try with any available format
            {
                'format': 'worst/best',
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            },
            # Try with basic options and any format
            {
                'format': '18/worst/best',  # Format 18 is usually available
                'quiet': True,
                'no_warnings': True,
            }
        ]
        
        for i, config in enumerate(alternative_configs):
            try:
                logger.info(f"Trying alternative extraction method {i+1}/{len(alternative_configs)}")
                with yt_dlp.YoutubeDL(config) as ydl:
                    info = ydl.extract_info(source, download=False)
                    logger.info(f"Alternative extraction method {i+1} succeeded")
                    return info['url']
            except Exception as e:
                logger.warning(f"Alternative method {i+1} failed: {str(e)}")
                continue
        
        # If all alternatives fail, raise the original error with helpful message
        raise Exception(
            "YouTube format extraction failed on production server. This can happen due to:\n"
            "1. Network restrictions on Railway servers\n"
            "2. Video format availability differences\n"
            "3. Geographic restrictions\n\n"
            "Try with a different YouTube video or contact support if this persists."
        )

    def run(self, source: str, is_url: bool = True) -> str:
        """Starts the pipeline and returns the reassembled transcript."""
        start_time = time.time()
        
        # Cleanup old chunks
        for f in glob.glob(str(self.chunk_dir / "*.wav")):
            try: os.remove(f)
            except: pass

        # Prepare ffmpeg command
        # resample to 16kHz, mono, segment every X seconds
        ffmpeg_cmd = [
            "ffmpeg", "-i", "pipe:0" if is_url else source,
            "-ar", "16000", "-ac", "1", "-f", "segment",
            "-segment_time", str(self.segment_time),
            "-reset_timestamps", "1",
            str(self.chunk_dir / "chunk_%03d.wav")
        ]

        # Use 4 threads for parallel transcription
        with ThreadPoolExecutor(max_workers=4) as executor:
            monitor_thread = threading.Thread(target=self.monitor_chunks, args=(executor,))
            monitor_thread.start()

            if is_url:
                # Streaming from yt-dlp with bot bypass
                try:
                    # Get yt-dlp options (with bypass if available)
                    if self.bypass_manager:
                        ydl_opts = self.bypass_manager.get_ydl_options(attempt=0)
                        logger.info(f"Starting YouTube download with bot bypass: {source}")
                    else:
                        ydl_opts = {
                            'format': 'bestaudio/best',
                            'quiet': True,
                            'no_warnings': True,
                        }
                    
                    # Extract audio URL with retry logic
                    audio_url = self._extract_youtube_audio_url(source, ydl_opts)
                    
                    # pipe:0 -> ffmpeg
                    process = subprocess.Popen(["ffmpeg", "-i", audio_url] + ffmpeg_cmd[3:], 
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    _, _ = process.communicate()
                    
                    duration = time.time() - start_time
                    logger.info(f"YouTube download completed in {duration:.2f}s")
                    
                except Exception as e:
                    logger.error(f"YouTube download failed: {str(e)}")
                    
                    # Return user-friendly error if bypass manager available
                    if self.bypass_manager:
                        attempts = self.bypass_manager.config.max_retries + 1
                        error_msg = self.bypass_manager.get_user_friendly_error(e, attempts)
                        
                        # Add specific Railway/production guidance for bot detection
                        if "Sign in to confirm you're not a bot" in str(e):
                            error_msg += (
                                "\n\n🚨 PRODUCTION ENVIRONMENT DETECTED:\n"
                                "YouTube bot detection is common on cloud servers like Railway. "
                                "For reliable production transcription:\n"
                                "1. Export YouTube cookies using 'Get cookies.txt LOCALLY' browser extension\n"
                                "2. Upload cookies.txt to your Railway deployment\n"
                                "3. Set YOUTUBE_COOKIE_PATH environment variable in Railway dashboard\n"
                                "4. Alternatively, try a different video or wait a few minutes"
                            )
                        
                        return f"Transcription failed: {error_msg}"
                    else:
                        return f"Multimedia Critical Error: {str(e)}"
            else:
                # Local file source
                process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _, _ = process.communicate()

            self.is_ffmpeg_done = True
            monitor_thread.join()

        # Reassemble results
        assembled_text = ""
        for i in sorted(self.results.keys()):
            assembled_text += self.results[i] + " "
        
        # Cleanup
        for f in glob.glob(str(self.chunk_dir / "*.wav")):
            try: os.remove(f)
            except: pass
            
        return assembled_text.strip()

class MultimediaAssistantTool(BaseTool):
    name: str = "multimedia_transcription_tool"
    description: str = (
        "An optimized multimedia transcription engine. "
        "Downloads YouTube URL streams or local files, splits them into 16kHz mono chunks in real-time, "
        "and transcribes them in parallel for maximum speed."
    )
    args_schema: Type[BaseModel] = MultimediaProcessorInput

    def _run(self, youtube_url: Optional[str] = None, media_path: Optional[str] = None) -> str:
        try:
            # Initialize bot bypass configuration
            config = BotBypassConfig.from_env()
            bypass_manager = BotBypassManager(config)
            
            # Create manager with bot bypass support
            manager = StreamingTranscriptionManager(
                segment_time=120,  # 2-minute chunks for better context
                bypass_manager=bypass_manager
            )
            
            if youtube_url:
                logger.info(f"Transcribing YouTube video: {youtube_url}")
                return manager.run(youtube_url, is_url=True)
            elif media_path and os.path.exists(media_path):
                logger.info(f"Transcribing local file: {media_path}")
                return manager.run(media_path, is_url=False)
            else:
                return "Error: No valid source provided for transcription."
                
        except Exception as e:
            logger.error(f"Multimedia tool error: {str(e)}")
            return f"Multimedia Critical Error: {str(e)}"

# Alias for backward compatibility if needed in crew/yaml
YouTubeVideoDownloaderTool = MultimediaAssistantTool