import os
import pyaudio
from google.cloud import speech_v1p1beta1 as speech
import queue
import threading

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_key.json"

client = speech.SpeechClient()

RATE = 16000  
CHUNK = int(RATE / 10)
FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_DEVICE_INDEX = None

audio_queue = queue.Queue()

def callback(in_data, frame_count, time_info, status):
    """Callback function to receive audio stream."""
    audio_queue.put(in_data)
    return None, pyaudio.paContinue

def listen_for_color():
    """Listen continuously and print everything, with special handling for 'color of'."""
    
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=INPUT_DEVICE_INDEX,
        stream_callback=callback
    )
    
    stream.start_stream()
    print("Listening...")

    def audio_generator():
        """Generate audio chunks for Google Cloud Speech."""
        while True:
            chunk = audio_queue.get()
            if chunk is None:
                return
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    streaming_config = speech.StreamingRecognitionConfig(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="en-US",
        ),
        interim_results=False
    )

    responses = client.streaming_recognize(streaming_config, audio_generator())

    for response in responses:
        for result in response.results:
            text = result.alternatives[0].transcript.lower()
            
            print(f"audio: {text}")
            
            if "color of" in text:
                print(f"!!!!! {text}")

threading.Thread(target=listen_for_color, daemon=True).start()

while True:
    pass
