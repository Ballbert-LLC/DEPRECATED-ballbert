from Hal.Voice import Voice
import speech_recognition as sr


def list_microphones():
    mic_list = sr.Microphone.list_working_microphones()
    print(mic_list)


list_microphones()

# voice = Voice()


# def callback(text, error):
#     print(text)


# voice.start(callback=callback)
