import speech_recognition as sr


def list_microphones():
    mic_list = sr.Microphone.list_microphone_names()
    for index, mic_name in enumerate(mic_list):
        print("Microphone {}: {}".format(index, mic_name))


list_microphones()


class ASR:
    def start():
        while True:
            input("Press Enter to continue...")
            # Create a recognizer object
            r = sr.Recognizer()

            # Define the microphone as the source
            mic = sr.Microphone(device_index=1)

            # Adjust the microphone sensitivity if needed
            mic.energy_threshold = 5000

            # Print the list of available microphones (optional)
            # print(sr.Microphone.list_microphone_names())

            # Start recording from the microphone
            with mic as source:
                print("Say something...")
                audio = r.listen(source)

            try:
                # Use Google Speech Recognition to transcribe the audio
                text = r.recognize_google(audio)
                print("Transcription: " + text)

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")

            except sr.RequestError as e:
                print(
                    "Could not request results from Google Speech Recognition service; {0}".format(
                        e
                    )
                )


asr = ASR()

asr.start()
