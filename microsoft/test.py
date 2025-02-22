import azure.cognitiveservices.speech as speechsdk

API_KEY = "key"
REGION = "eastus"


def speech_to_text(audio_filename):

    speech_config = speechsdk.SpeechConfig(subscription=API_KEY, region=REGION)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_filename)
    

    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    

    print("Recognizing speech...")
    result = recognizer.recognize_once()


    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")


audio_filename = "test.wav"
speech_to_text(audio_filename)