import platform
import pvporcupine
import speech_recognition as sr
from pvrecorder import PvRecorder
import threading
from Config import Config

config = Config()


class Voice:
    def __init__(self) -> None:
        print(config["PORQUPINE_API_KEY"])

        system = platform.system()

        if system == "Linux":
            path = "./Hal/Voice/Ball-Bert_en_raspberry-pi_v2_2_0.ppn"
        elif system == "Windows":
            path = "./Hal/Voice/Ball-Bert_en_windows_v2_2_0.ppn"
        elif system == "Darwin":
            path = "./Hal/Voice/Ball-Bert_en_mac_v2_2_0.ppn"
        else:
            raise Exception("Unsupported system")

        self.porcupine = pvporcupine.create(
            access_key=config["PORQUPINE_API_KEY"],
            keyword_paths=[path],
        )

        # Create PvRecorder object with a larger buffer size
        print(config["PV_MIC"], self.porcupine.frame_length)
        self.recorder = PvRecorder(
            device_index=config["PV_MIC"],
            frame_length=self.porcupine.frame_length,
        )

        # print(sr.Microphone.list_microphone_names()[config["SR_MIC"]])
        # with sr.Microphone(config["SR_MIC"]) as source:
        #     recognizer.adjust_for_ambient_noise(source)

    def start(self, callback):
        # Start recording
        self.recorder.start()
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 3000

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
                callback(text, None)

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                callback("", "Google Speech Recognition could not understand audio")

            except sr.RequestError as e:
                print(
                    "Could not request results from Google Speech Recognition service; {0}".format(
                        e
                    )
                )
                callback("", e)
