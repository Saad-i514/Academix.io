import os
import subprocess
import time
import glob
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Type, Optional, List, Dict
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import yt_dlp
from faster_whisper import WhisperModel

# Global Whisper Model (Thread-safe for inference)
MODEL = WhisperModel("base", device="cpu", compute_type="int8")

class MultimediaProcessorInput(BaseModel):
    youtube_url: Optional[str] = Field(None, description="YouTube video URL")
    media_path: Optional[str] = Field(None, description="Path to a local audio or video file")

class StreamingTranscriptionManager:
    """Manages the real-time pipe from yt-dlp/file to ffmpeg chunks to faster-whisper."""
    
    def __init__(self, segment_time: int = 30):
        self.segment_time = segment_time
        self.chunk_dir = Path("transcription_chunks")
        self.chunk_dir.mkdir(exist_ok=True)
        self.results: Dict[int, str] = {}
        self.active_workers = 0
        self.lock = threading.Lock()
        self.is_ffmpeg_done = False

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

    def run(self, source: str, is_url: bool = True) -> str:
        """Starts the pipeline and returns the reassembled transcript."""
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
                # Streaming from yt-dlp
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(source, download=False)
                    audio_url = info['url']
                    
                    # pipe:0 -> ffmpeg
                    process = subprocess.Popen(["ffmpeg", "-i", audio_url] + ffmpeg_cmd[3:], 
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    _, _ = process.communicate()
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
            manager = StreamingTranscriptionManager(segment_time=120) # 2-minute chunks for better context
            
            if youtube_url:
                return manager.run(youtube_url, is_url=True)
            elif media_path and os.path.exists(media_path):
                return manager.run(media_path, is_url=False)
            else:
                return "Error: No valid source provided for transcription."
                
        except Exception as e:
            return f"Multimedia Critical Error: {str(e)}"

# Alias for backward compatibility if needed in crew/yaml
YouTubeVideoDownloaderTool = MultimediaAssistantTool