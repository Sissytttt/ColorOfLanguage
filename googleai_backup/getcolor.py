import os
from dotenv import load_dotenv
import pyaudio
from google.cloud import speech_v1p1beta1 as speech
import queue
import threading
from google.cloud import language_v1

import speech_recognition as sr
import openai
import time


os.environ["GRPC_VERBOSITY"] = "ERROR"  # Only show errors
os.environ["GRPC_TRACE"] = "none"  # Disable trace logs

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_key.json"

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

speech_client = speech.SpeechClient()

language_client = language_v1.LanguageServiceClient()

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

    responses = speech_client.streaming_recognize(streaming_config, audio_generator())

    for response in responses:
        for result in response.results:
            text = result.alternatives[0].transcript.lower()

            print(f"audio: {text}")

            if "color of" in text:
                print(f"Color prompt: {text}")
                color_info = get_rgb_from_chatgpt(text)
                print(f"return color value: {color_info}")
    

def get_rgb_from_chatgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a color expert. Respond only with an RGB tuple."},
            {"role": "user", "content": f"The user says {prompt}, please give the RGB value of the color that is most relevant with its color."}
        ]
    )
    rgb_string = response.choices[0].message.content.strip()
    return tuple(map(int, rgb_string.strip('()').split(',')))


threading.Thread(target=listen_for_color, daemon=True).start()

while True:
    pass
