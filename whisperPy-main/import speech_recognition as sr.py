import speech_recognition as sr
from dotenv import load_dotenv
import openai
import time

# Configure OpenAI API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# LED matrix dimensions
WIDTH = 32
HEIGHT = 32


def listen_and_print():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... (Speak into the microphone)")
        while True:
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")


def listen_for_color():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for 'color of...'")
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio).lower()
        if text.startswith("color of"):
            return text[9:].strip()  # Return the text after "color of"
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
    
    return None

def get_rgb_from_chatgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a color expert. Respond only with an RGB tuple."},
            {"role": "user", "content": f"What is the RGB value for the color of {prompt}?"}
        ]
    )
    rgb_string = response.choices[0].message.content.strip()
    return tuple(map(int, rgb_string.strip('()').split(',')))

def generate_frame(rgb_value, width=WIDTH, height=HEIGHT):
    frame = []
    for _ in range(height * width):
        frame.extend(rgb_value)
    return frame

def format_frame_output(frame):
    return f"frame{frame}"

# Main loop
while True:
    color_prompt = listen_for_color()
    if color_prompt:
        rgb_value = get_rgb_from_chatgpt(color_prompt)
        frame = generate_frame(rgb_value)
        output = format_frame_output(frame)
        print(output)  
    time.sleep(0.1)

    # listen_and_print()