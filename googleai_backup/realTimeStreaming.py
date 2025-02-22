#  real time streaming

import os
import pyaudio
from google.cloud import speech_v1p1beta1 as speech
import threading

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp_key.json'

client = speech.SpeechClient()

p = pyaudio.PyAudio()

RATE = 16000 
CHUNK = int(RATE / 10) 
FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_DEVICE_INDEX = None

def generate_audio_stream():
    """Stream audio chunks from the microphone to Google Cloud Speech."""
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=INPUT_DEVICE_INDEX)
    print("Recording...")
    while True:
        # Capture from microphone
        data = stream.read(CHUNK)
        yield data

def real_time_transcribe():
    """Real-time transcription of microphone audio using Google Cloud Speech-to-Text."""
    streaming_config = speech.StreamingRecognitionConfig(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="en-US",
        ),
        interim_results=True,
    )

    # streaming
    requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in generate_audio_stream())
    responses = client.streaming_recognize(streaming_config, requests)

    for response in responses:
        for result in response.results:
            # Print the transcriptions as they arrive
            print(f"Transcript: {result.alternatives[0].transcript}")
            if result.is_final:
                print(f"Final Transcript: {result.alternatives[0].transcript}")

# Run transcription in a separate thread to allow continuous listening
transcription_thread = threading.Thread(target=real_time_transcribe)
transcription_thread.start()
