from faster_whisper import WhisperModel

model = WhisperModel("base")

def transcribe_audio(file_path):
    segments, _ = model.transcribe(file_path)
    text = ""

    for segment in segments:
        text += segment.text

    return text
if __name__ == "__main__":
    audio_file = "audio.mp3"  # Path to the downloaded audio file
    transcription = transcribe_audio(audio_file)
    print("Transcription:")
    print(transcription)