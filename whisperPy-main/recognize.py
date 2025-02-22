from openai import OpenAI
import json
import sys
import os
import re
import serial
import time
from recorder import live_speech

# Set the API key for accessing OpenAI's services
api_key = 'SW018oawr21E6Fao8OlcT3BlbkFJHmsveLSivkahk6TilRAD'
chatgpt = OpenAI(api_key=api_key)

# LED matrix dimensions
WIDTH = 32
HEIGHT = 32


# Initial system message that sets the role of the assistant (ChatGPT)
messages = [
    {
        "role": "system",
        "content": "You are a voice-controlled color generator for an LED light matrix. The user will ask for the color of something, which can be anything from a reference to a specific object (blue night sky or red apple), to something more abstract (math, staying in morning). Generate a specific, visually appealing, accurate color that will show up beautifully on an LED in the form of RGB values as 'R,G,B'. Do not generate anything but the RBG values." 
    },
]

def detect_phrase(command: str, phrase: str) -> bool:
    """
    Detects whether a specific phrase is present in the command.
    Removes punctuation and converts to lowercase before checking.
    """
    command = re.sub(r"[,\.!?]", "", command.lower())
    phrase = re.sub(r"[,\.!?]", "", phrase.lower())
    return phrase in command

def generate_frame(rgb_value, width=WIDTH, height=HEIGHT):
    frame = []
    for _ in range(height * width):
        frame.extend(rgb_value)
    return frame

def format_frame_output(frame):
    return f"frame{frame}"

def send_frame_command(rgb_tuple, ser):
    """
    Generates a frame with the given RGB color and sends it to main.py.
    """
    frame = generate_frame(rgb_tuple)
    formatted_output = format_frame_output(frame)
    ser.write((formatted_output + '\n').encode('utf-8'))
    print(f"Sent to main.py: {formatted_output}")


def main():
    # Check if the required file for wake-up words exists
    with open("wakeup_words.json", "r") as f:
        wakeup_words = json.load(f)

    # Set the specific wake-up phrase to listen for
    wakeup_phrase = "color of"

    # Open serial connection to Arduino
    ser = serial.Serial('/dev/cu.usbmodem101', 9600)  # Adjust the port as necessary
    time.sleep(2)  # Wait for the serial connection to initialize

    current_color = None

    while True:
        # Continuously listen for the wake-up phrase
        print("Listening for the wake-up phrase...")
        for message in live_speech():
            if detect_phrase(message, wakeup_phrase):
                print(f"Detected phrase: {message}")

                # Process the command after detecting the wake-up phrase
                complete_command = message
                
                # Add the detected command to the conversation history
                messages.append(
                    {
                        "role": "user",
                        "content": complete_command
                    }
                )

                # Send the conversation history to OpenAI and get a response
                response = chatgpt.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )

                response_text = response.choices[0].message.content.strip()
                print(f"ChatGPT: {response_text}")

                # Add the assistant's response to the conversation history
                messages.append(
                    {
                        "role": "assistant",
                        "content": response_text
                    }
                )
                
                # Process the response for RGB values
                rgb_values = response_text.split(',')
                if len(rgb_values) == 3 and all(value.isdigit() for value in rgb_values):
                    rgb_tuple = (int(rgb_values[0]), int(rgb_values[1]), int(rgb_values[2]))
                    send_frame_command(rgb_tuple, ser)
                else:
                    print("Response did not contain valid RGB values.")

if __name__ == "__main__":
    main()



