"""
https://platform.openai.com/docs/guides/speech-to-text
https://cookbook.openai.com/examples/speech_transcription_methods
https://platform.openai.com/docs/guides/realtime-transcription#realtime-transcription-sessions
"""

import openai
import sounddevice as sd
import soundfile as sf
import numpy as np

print(sd.query_devices())

client = openai.OpenAI(api_key="MY_KEY")

duration=5
fs=16000

def record_audio(filename="audio.wav"):
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16', device=8)
    sd.wait()
    print("Done.")
    sf.write(filename, audio, fs)
    return audio.flatten().tobytes()

def transcribe(filename="audio.wav"):
    with open(filename, "rb") as f:
        response = client.audio.translations.create(
            file=f,
            model="whisper-1"
        )
    return response.text

if __name__ == "__main__":
    record_audio()
    text = transcribe()

    print("transcription result :")

    print(text)