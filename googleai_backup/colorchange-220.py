# v differentiate  1. new agent session and send msg; 2. send msg in a session; 3. ignore
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

is_speaking = False
in_speaking_session = False
# in_speaking_session == True -> keep sending msg to the agent
# in_speaking_session == False  -> create a new agent next time


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
    global last_speech_time, light_on, in_speaking_session
    for response in responses:
        for result in response.results:
            if result.is_final:                                      # final result
                text = result.alternatives[0].transcript.lower()
                last_speech_time = time.time()

                print(f"Final Audio: {text}") 
                
                if is_speaking and in_speaking_session == False and "color" in text:
                    create_agent_and_get_rgb(text)
                    # color_info = create_agent_and_get_rgb(text)
                    # print(f"Return color value: {color_info}")
                    in_speaking_session = True

                elif is_speaking and in_speaking_session == True:
                    send_msg_to_and_get_rgb()
                
                elif is_speaking == False:
                    in_speaking_session = False
                
                else:
                    pass
            else:                                                     # intermediate result
                text = result.alternatives[0].transcript.lower()
                last_speech_time = time.time()
                if "color" in text:
                    if light_on == False:
                        light_on = True
                        print("light_on")

def check_speaking():
    """Continuously check if the user is speaking."""
    global is_speaking, last_speech_time, light_on, in_speaking_session
    while True:
        if time.time() - last_speech_time > speech_timeout and is_speaking:
            is_speaking = False
            in_speaking_session = False
            light_on = False
            print("User stops speaking")
        elif time.time() - last_speech_time <= speech_timeout and not is_speaking:
            is_speaking = True
            print("User starts speaking")
        time.sleep(0.5)


def create_agent_and_get_rgb(prompt):
    """Query GPT for RGB values based on the prompt."""
    print("创+发")


def send_msg_to_and_get_rgb():
    print("发")


def nothing():
    print("什么都不干")


# speech status checking in a separate thread
speech_check_thread = threading.Thread(target=check_speaking, daemon=True)
speech_check_thread.start()

while True:
    listen()
