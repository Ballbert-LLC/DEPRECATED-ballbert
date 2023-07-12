import platform
import pvporcupine
import speech_recognition as sr
from pvrecorder import PvRecorder

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

        self.recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)

        self.recognizer.energy_threshold = 3000

    def start(self, callback):
        # Start recording
        self.recorder.start()

        while True:
            # Read PCM audio data
            audio_frames = self.recorder.read()

            # Process audio with Porcupine
            keyword_index = self.porcupine.process(audio_frames)

            if keyword_index >= 0:
                print("Keyword detected")

                self.recorder.stop()
                # Start transcribing the user's speech
                with sr.Microphone() as source:
                    try:
                        # Capture speech input
                        audio = self.recognizer.listen(
                            source,
                        )

                        print("audio", audio, "type", type(audio))
                        # Use Google Speech Recognition to transcribe audio
                        text = self.recognizer.recognize_google(audio)
                        print("text", text)
                        callback(text, None)

                    except sr.UnknownValueError as e:
                        print("unknown error occurred when trying to transcribe audio")
                        callback("", e)

                    except sr.RequestError as e:
                        print(
                            e, "request error occurred when trying to transcribe audio"
                        )
                        callback("", e)

                    except sr.WaitTimeoutError as e:
                        print(
                            e,
                            "wait timeout error occurred when trying to transcribe audio",
                        )
                        callback("", e)
                self.recorder.start()
            else:
                continue
