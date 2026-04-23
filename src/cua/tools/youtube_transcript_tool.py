"""Free YouTube transcription using YouTube Transcript API.

This tool uses the official YouTube Transcript API which:
- Is completely free
- Has no bot detection issues
- Works reliably on Railway and all cloud platforms
- Doesn't require cookies or proxies
- Provides instant transcripts without downloading videos
"""

import logging
import re
import time
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

logger = logging.getLogger("Academix.YouTubeTranscript")

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False
    logger.warning("youtube-transcript-api not installed. Install with: pip install youtube-transcript-api")


class YouTubeTranscriptInput(BaseModel):
    """Input for YouTube transcript tool."""
    youtube_url: str = Field(..., description="YouTube video URL")
    language: str = Field(default="en", description="Preferred transcript language code (e.g., 'en', 'es', 'fr')")


class YouTubeTranscriptTool(BaseTool):
    """Tool for getting YouTube video transcripts using the free Transcript API.
    
    This tool:
    - Uses YouTube's official Transcript API (completely free)
    - Works on all platforms including Railway
    - No bot detection issues
    - No cookies or proxies needed
    - Instant results without video download
    """
    
    name: str = "YouTube Transcript Tool"
    description: str = (
        "Get transcripts from YouTube videos using the free YouTube Transcript API. "
        "Works reliably on all platforms without bot detection issues. "
        "Supports multiple languages and automatic fallback."
    )
    args_schema: type[BaseModel] = YouTubeTranscriptInput
    
    def _run(self, youtube_url: str, language: str = "en") -> str:
        """Get transcript from YouTube video.
        
        Args:
            youtube_url: YouTube video URL
            language: Preferred language code (default: 'en')
            
        Returns:
            Transcript text or error message
        """
        if not TRANSCRIPT_API_AVAILABLE:
            return (
                "YouTube Transcript API is not installed. "
                "Please install it with: pip install youtube-transcript-api"
            )
        
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(youtube_url)
            if not video_id:
                return f"Invalid YouTube URL: {youtube_url}"
            
            logger.info(f"Fetching transcript for video: {video_id}")
            
            # Create API instance
            api = YouTubeTranscriptApi()
            
            # Try to get transcript in preferred language with retry logic
            max_retries = 3
            retry_delay = 2  # Start with 2 seconds
            
            for attempt in range(max_retries):
                try:
                    try:
                        transcript_list = api.fetch(video_id, languages=[language])
                        logger.info(f"Successfully fetched transcript in {language}")
                    except NoTranscriptFound:
                        # Fallback to any available transcript
                        logger.info(f"No transcript in {language}, trying any available language")
                        transcript_list = api.fetch(video_id)
                        logger.info("Successfully fetched transcript in available language")
                    
                    # Combine all transcript segments into full text
                    full_transcript = " ".join([snippet.text for snippet in transcript_list])
                    
                    # Clean up the transcript
                    full_transcript = self._clean_transcript(full_transcript)
                    
                    logger.info(f"Transcript length: {len(full_transcript)} characters")
                    return full_transcript
                    
                except Exception as e:
                    error_msg = str(e)
                    # Check if it's a rate limit error
                    if "too many requests" in error_msg.lower() or "blocked" in error_msg.lower():
                        if attempt < max_retries - 1:
                            logger.warning(f"Rate limited (attempt {attempt + 1}/{max_retries}). Waiting {retry_delay}s before retry...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                    raise
            
        except TranscriptsDisabled:
            return (
                f"Transcripts are disabled for this video: {youtube_url}\n\n"
                "This video does not have captions/subtitles available. "
                "The video owner has either disabled captions or hasn't provided them."
            )
        
        except VideoUnavailable:
            return (
                f"Video is unavailable: {youtube_url}\n\n"
                "The video may be private, deleted, or restricted in your region."
            )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Transcript fetch failed: {error_msg}")
            
            # Check if it's a rate limit error
            if "too many requests" in error_msg.lower() or "blocked" in error_msg.lower():
                return (
                    f"YouTube has rate-limited requests from this IP.\n\n"
                    f"Error: {error_msg}\n\n"
                    "Solutions:\n"
                    "1. Wait 15-30 minutes and try again\n"
                    "2. Use a different YouTube video\n"
                    "3. Configure a free proxy (Webshare offers 10 free proxies)\n"
                    "4. Contact support if this persists"
                )
            
            return (
                f"Failed to fetch transcript for {youtube_url}\n\n"
                f"Error: {error_msg}\n\n"
                "Possible reasons:\n"
                "1. Video has no captions/subtitles\n"
                "2. Video is private or restricted\n"
                "3. Invalid video URL\n"
                "4. Temporary YouTube API issue"
            )
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID or None if invalid
        """
        # Support various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If URL is already just the video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        return None
    
    def _clean_transcript(self, transcript: str) -> str:
        """Clean up transcript text.
        
        Args:
            transcript: Raw transcript text
            
        Returns:
            Cleaned transcript
        """
        # Remove extra whitespace
        transcript = re.sub(r'\s+', ' ', transcript)
        
        # Remove common caption artifacts
        transcript = re.sub(r'\[.*?\]', '', transcript)  # Remove [Music], [Applause], etc.
        transcript = re.sub(r'\(.*?\)', '', transcript)  # Remove (inaudible), etc.
        
        # Clean up spacing
        transcript = transcript.strip()
        
        return transcript
    
    def get_available_languages(self, youtube_url: str) -> List[str]:
        """Get list of available transcript languages for a video.
        
        Args:
            youtube_url: YouTube video URL
            
        Returns:
            List of available language codes
        """
        if not TRANSCRIPT_API_AVAILABLE:
            return []
        
        try:
            video_id = self._extract_video_id(youtube_url)
            if not video_id:
                return []
            
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            languages = []
            
            for transcript in transcript_list:
                languages.append(transcript.language_code)
            
            return languages
        except Exception as e:
            logger.error(f"Failed to get available languages: {e}")
            return []


def get_youtube_transcript(youtube_url: str, language: str = "en") -> str:
    """Convenience function to get YouTube transcript.
    
    Args:
        youtube_url: YouTube video URL
        language: Preferred language code (default: 'en')
        
    Returns:
        Transcript text or error message
    """
    tool = YouTubeTranscriptTool()
    return tool._run(youtube_url=youtube_url, language=language)
