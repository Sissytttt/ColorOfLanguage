import azure.cognitiveservices.speech as speechsdk

API_KEY = "key"
REGION = "eastus"


def speech_to_text_realtime():

    speech_config = speechsdk.SpeechConfig(subscription=API_KEY, region=REGION)
    

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    

    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    

    def recognized_handler(sender, event):
        print(f"Recognized: {event.result.text}")
    

    recognizer.recognized.connect(recognized_handler)
    

    print("Start speaking...")
    recognizer.start_continuous_recognition()


    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Recognition stopped.")
        recognizer.stop_continuous_recognition()


speech_to_text_realtime()
