import yt_dlp

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'ffmpeg_location': r'C:\ffmpeg\ffmpeg-8.1-essentials_build\bin'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return "audio.mp3"

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example YouTube URL
    audio_file = download_audio(url)
    print(f"Audio downloaded: {audio_file}")