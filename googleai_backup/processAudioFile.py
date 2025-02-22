# read audio file
from google.cloud import speech_v1 as speech
import os
from pydub import AudioSegment
import wave


with wave.open("test.wav", "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        print(f"sample rate: {(sample_rate)}")


client = speech.SpeechClient.from_service_account_file("gcp_key.json")

def convert_to_mono(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_channels(1)
    audio.export(output_file, format="wav")
    print("converted to mono")

def transcript_audio(input_file):
    with open(input_file, "rb") as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = sample_rate,
            language_code = "en-US"
        )
        response = client.recognize(config=config, audio=audio)
        for result in response.results:
            print(f"transcript: {result.alternatives[0].transcript}")
            print(f"confidence: {result.alternatives[0].confidence}")
    return response


convert_to_mono("test.wav", "audio_sample.wav")
transcript_audio("audio_sample.wav")