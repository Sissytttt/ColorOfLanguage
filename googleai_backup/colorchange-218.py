# v detect start & stop speaking using intermediate speech detection
# todo: use start & stop to control GPT agent & msging 

import os
from dotenv import load_dotenv
import pyaudio
from google.cloud import speech_v1p1beta1 as speech
import queue
import threading
import time
import openai

os.environ["GRPC_VERBOSITY"] = "ERROR"  # Only show errors
os.environ["GRPC_TRACE"] = "none"  # Disable trace logs

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_key.json"
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
speech_client = speech.SpeechClient()

speaking_stops = True
last_speech_time = 0
speech_timeout = 3 

RATE = 16000
CHUNK = int(RATE / 10)
FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_DEVICE_INDEX = None


light_on = False

audio_queue = queue.Queue()

def callback(in_data, frame_count, time_info, status):
    """Callback function to receive audio stream."""
    audio_queue.put(in_data)
    return None, pyaudio.paContinue


def audio_generator():
    """Generate audio chunks for Google Cloud Speech."""
    while True:
        chunk = audio_queue.get()
        if chunk is None:
            return
        yield speech.StreamingRecognizeRequest(audio_content=chunk)


def listen():
    """Listen continuously and handle speech recognition."""

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

    streaming_config = speech.StreamingRecognitionConfig(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="en-US",
        ),
        interim_results=True
    )

    responses = speech_client.streaming_recognize(streaming_config, audio_generator())
    detect_color(responses)


def detect_color(responses):
    """Detect 'color' keyword and handle recognition results."""
    global last_speech_time, light_on
    for response in responses:
        for result in response.results:
            if result.is_final: # final result
                text = result.alternatives[0].transcript.lower()
                last_speech_time = time.time()

                print(f"Final Audio: {text}") 

                if "color" in text:
                    print(f"Color prompt: {text}")
                    color_info = create_agent_and_get_rgb(text)
                    print(f"Return color value: {color_info}")

            else: # intermediate result
                text = result.alternatives[0].transcript.lower()
                last_speech_time = time.time()
                if "color" in text:
                    if light_on == False:
                        light_on = True
                        print("light_on")

def check_speaking():
    """Continuously check if the user is speaking."""
    global speaking_stops, last_speech_time
    while True:
        if time.time() - last_speech_time > speech_timeout and speaking_stops:
            speaking_stops = False
            print("User stops speaking")
        elif time.time() - last_speech_time <= speech_timeout and not speaking_stops:
            speaking_stops = True
            print("User starts speaking")
        time.sleep(0.5)


def create_agent_and_get_rgb(prompt):
    """Query GPT for RGB values based on the prompt."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a color expert. Respond only with an RGB tuple."},
            {"role": "user", "content": f"The user says {prompt}, please give the RGB value of the color that is most relevant with its color."}
        ]
    )
    rgb_string = response.choices[0].message.content.strip()
    return tuple(map(int, rgb_string.strip('()').split(',')))


# speech status checking in a separate thread
speech_check_thread = threading.Thread(target=check_speaking, daemon=True)
speech_check_thread.start()

while True:
    listen()
