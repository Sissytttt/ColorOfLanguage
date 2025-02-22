# Real time


import openai
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import queue
import wave
import os
import time

# OpenAI API Key (Replace with your actual key)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# Audio recording settings
SAMPLE_RATE = 16000  # Whisper works best with 16kHz audio
CHANNELS = 1         # Mono audio
DURATION = 2         # Increased duration to avoid "too short" error
BLOCK_SIZE = 1024    # Buffer size for streaming audio

# Queue to store recorded audio
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Callback function to capture audio and store it in the queue."""
    if status:
        print("Status:", status)
    audio_queue.put(indata.copy())

def record_and_transcribe():
    print("🎤 Listening... Speak now!")

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16", callback=audio_callback):
        while True:
            audio_chunk = []

            # Collect enough data for DURATION seconds
            for _ in range(int(DURATION * SAMPLE_RATE / BLOCK_SIZE)):
                audio_chunk.append(audio_queue.get())

            # Convert to numpy array
            audio_data = np.concatenate(audio_chunk, axis=0)

            # Debugging: Check if audio was captured
            print("Audio data shape:", audio_data.shape)
            print("Max amplitude:", np.max(audio_data))

            # If silent, skip transcription
            if np.max(audio_data) == 0:
                print("⚠️ No sound detected! Try speaking louder.")
                continue

            # Save as WAV file
            wav_file = f"temp_{int(time.time())}.wav"  # Unique filename
            with wave.open(wav_file, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data.tobytes())

            # Debugging: Check if file exists and has data
            print("File exists:", os.path.exists(wav_file))
            print("File size:", os.path.getsize(wav_file))

            # Send to OpenAI Whisper API
            with open(wav_file, "rb") as file:
                try:
                    response = openai.Audio.transcribe("whisper-1", file, api_key=OPENAI_API_KEY)
                    print("📝 You said:", response["text"])  # Print transcription immediately
                except Exception as e:
                    print("Error:", e)

            # Clean up temporary file
            os.remove(wav_file)

# Run the real-time transcription
record_and_transcribe()