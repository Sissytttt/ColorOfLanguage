# not real time

import openai
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import wave
import time

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Audio settings
SAMPLE_RATE = 16000  
CHANNELS = 1
DURATION = 10

def record_and_transcribe():
    print("Listening... Speak now!")

    # Record audio for at least DURATION seconds
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16")
    sd.wait()  # Wait until recording is done

    # Save as a WAV file
    with wave.open("temp.wav", "wb") as audio_wav:
        audio_wav.setnchannels(CHANNELS)
        audio_wav.setsampwidth(2)
        audio_wav.setframerate(SAMPLE_RATE)
        audio_wav.writeframes(audio_data.tobytes())

    # Send the recorded audio to OpenAI Whisper API
    with open("temp.wav", "rb") as file:
        response = openai.Audio.transcribe("whisper-1", file, api_key=OPENAI_API_KEY)

    print("You said:", response["text"])

# Run transcription
record_and_transcribe()
