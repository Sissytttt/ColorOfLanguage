# sending RGB values using one queue

import os
from dotenv import load_dotenv
import pyaudio
from google.cloud import speech_v1p1beta1 as speech
import queue
import threading
import time
import openai
import serial
import serial.tools.list_ports


arduino = serial.Serial(port='/dev/cu.usbmodem21301', baudrate=9600, timeout=1)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_key.json"
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
conversation_history = [
    {"role": "system", "content": "You are a color expert. Respond only with an RGB tuple."}
]

ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"Found Port: {port.device} - {port.description}")

speech_client = speech.SpeechClient()

is_speaking = False
in_speaking_session = False
light_on = False
last_speech_time = 0
speech_timeout = 5


serial_queue = queue.Queue()

RATE = 16000
CHUNK = int(RATE / 10)
FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_DEVICE_INDEX = None
audio_queue = queue.Queue()

def serial_manager():
    while True:
        rgb_color = serial_queue.get() 
        if isinstance(rgb_color, tuple) and len(rgb_color) == 3:
            r, g, b = rgb_color
            color_str = f"{r},{g},{b}\n"
            arduino.write(color_str.encode()) 
            print(f"Sent to Arduino: {color_str}")
        else:
            print(f"Invalid RGB format: {rgb_color}")

def send_rgb_to_arduino(rgb_color):
    serial_queue.put(rgb_color)

serial_thread = threading.Thread(target=serial_manager, daemon=True)
serial_thread.start()

def callback(in_data, frame_count, time_info, status):
    audio_queue.put(in_data)
    return None, pyaudio.paContinue

def audio_generator():
    while True:
        chunk = audio_queue.get()
        if chunk is None:
            return
        yield speech.StreamingRecognizeRequest(audio_content=chunk)


def listen():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
        frames_per_buffer=CHUNK, input_device_index=INPUT_DEVICE_INDEX,
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
    global last_speech_time, light_on, in_speaking_session
    for response in responses:
        for result in response.results:
            if result.is_final:
                text = result.alternatives[0].transcript.lower()
                last_speech_time = time.time()
                print(f"Final Audio: {text}") 

                if is_speaking and not in_speaking_session and "color" in text:
                    color_info = create_agent_and_get_rgb(text)
                    print(f"Return color value: {color_info}")
                    send_rgb_to_arduino(color_info) 
                    in_speaking_session = True

                elif is_speaking and in_speaking_session:
                    color_info = send_msg_to_and_get_rgb(text)
                    print(f"Return color value: {color_info}")
                    send_rgb_to_arduino(color_info)

                elif not is_speaking:
                    in_speaking_session = False

                else:
                    pass
            else:
                text = result.alternatives[0].transcript.lower()
                last_speech_time = time.time()
                if "color" in text and not light_on:
                    light_on = True
                    send_rgb_to_arduino((200, 200, 200))
                    print("light_on")


def check_speaking():
    global is_speaking, last_speech_time, light_on, in_speaking_session
    while True:
        if time.time() - last_speech_time > speech_timeout and is_speaking:
            is_speaking = False
            in_speaking_session = False
            light_on = False
            send_rgb_to_arduino((0, 0, 0))
            print("User stops speaking")
        elif time.time() - last_speech_time <= speech_timeout and not is_speaking:
            is_speaking = True
            print("User starts speaking")
        time.sleep(0.5)


def create_agent_and_get_rgb(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a color expert. Respond only with an RGB tuple."},
            {"role": "user", "content": f"The user says {prompt}, please give the RGB value of the color that is most relevant with its color."}
        ]
    )
    rgb_string = response.choices[0].message.content.strip()
    return tuple(map(int, rgb_string.strip('()').split(',')))


def send_msg_to_and_get_rgb(text):
    global conversation_history
    conversation_history.append({"role": "user", "content": text})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    rgb_string = response.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": rgb_string})

    return tuple(map(int, rgb_string.strip('()').split(',')))


speech_check_thread = threading.Thread(target=check_speaking, daemon=True)
speech_check_thread.start()


while True:
    listen()
