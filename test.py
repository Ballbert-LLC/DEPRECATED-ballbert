from Hal.Voice import Voice
import speech_recognition as sr


def list_microphones():
    mic_list = sr.Microphone.list_working_microphones()
    for index, mic_name in enumerate(mic_list):
        print(f"Microphone {index}: {mic_name}")


list_microphones()

# voice = Voice()


# def callback(text, error):
#     print(text)


# voice.start(callback=callback)
