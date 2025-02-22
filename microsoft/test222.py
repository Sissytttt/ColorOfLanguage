import azure.cognitiveservices.speech as speechsdk
import time

# Replace with your Azure Speech API key and region
API_KEY = "key"
REGION = "eastus"

def speech_to_text_realtime():
    # Set up the Speech API client
    speech_config = speechsdk.SpeechConfig(subscription=API_KEY, region=REGION)
    
    # Set up the audio configuration for microphone input
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    # Set up the recognizer
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Define a callback to handle real-time transcriptions
    def recognized_handler(sender, event):
        print(f"Event received: {event.result.reason}")  # Debugging output for event reason
        if event.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized: {event.result.text}")
        elif event.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")
    
    # Connect the event handler to the recognizer
    recognizer.recognized.connect(recognized_handler)
    
    # Start continuous speech recognition
    print("Start speaking...")
    recognizer.start_continuous_recognition()

    # Keep the program running while recognizing speech
    try:
        # Wait for the recognition to process continuously
        while True:
            time.sleep(1)  # Sleep to allow background processing
    except KeyboardInterrupt:
        # Stop recognition when the user interrupts
        print("Recognition stopped.")
        recognizer.stop_continuous_recognition()

# Start real-time transcription
speech_to_text_realtime()
