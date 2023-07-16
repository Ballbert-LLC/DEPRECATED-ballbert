import platform
import pvporcupine
import speech_recognition as sr
from pvrecorder import PvRecorder
import threading
from Config import Config

config = Config()


class Voice:
    def __init__(self) -> None:
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

        self.recorder = PvRecorder(
            device_index=config["PV_MIC"],
            frame_length=self.porcupine.frame_length,
        )

    def start(self, callback):
        mic = sr.Microphone(device_index=1)
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300

        with mic as source:
            print("source", source, "type", type(source), source.stream)
            # Start recording
            while True:
                self.recorder.start()

                audio_frames = self.recorder.read()

                # Process audio with Porcupine
                keyword_index = self.porcupine.process(audio_frames)

                if keyword_index >= 0:
                    self.recorder.stop()

                    audio = recognizer.listen(
                        source=source,
                    )

                    text = recognizer.recognize_google(audio)

                    threading.Thread(target=callback, args=(text, None)).start()

                else:
                    continue
