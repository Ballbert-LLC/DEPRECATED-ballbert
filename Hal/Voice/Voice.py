import platform
import pvporcupine
import pyaudio
import speech_recognition as sr
from pvrecorder import PvRecorder
import threading
from Config import Config
import numpy as np

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

    # def start(self, callback):
    #     mic = sr.Microphone(device_index=1, sample_rate=self.porcupine.sample_rate)
    #     recognizer = sr.Recognizer()
    #     recognizer.energy_threshold = 300

    #     with mic as source:
    #         print("source", source, "type", type(source), source.stream)
    #         # Start recording
    #         while True:
    #             audio_frames = source.stream.read(512)

    #             # convert audio frames to single channel, 16-bit PCM audio
    #             audio_data = np.frombuffer(audio_frames, dtype=np.int16)

    #             # Process audio with Porcupine
    #             keyword_index = self.porcupine.process(audio_data)

    #             if keyword_index >= 0:
    #                 print("Keyword detected")
    #                 audio = recognizer.listen(
    #                     source=source,
    #                 )

    #                 text = recognizer.recognize_google(audio)

    #                 threading.Thread(target=callback, args=(text, None)).start()

    #             else:
    #                 continue

    def test(self, callback):
        # the mics sample rate is 44100
        mic = sr.Microphone(device_index=1, sample_rate=16000)
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300

        # porcupines sampel rate is 16000

        with mic as source:
            while True:
                # Start recording
                audio_frames = source.stream.read(512)

                np_audio_data = np.frombuffer(audio_frames, dtype=np.int16)

                keyword_index = self.porcupine.process(np_audio_data)
                if keyword_index >= 0:
                    print("Keyword detected")
                    audio = recognizer.listen(
                        source=source,
                    )

                    text = recognizer.recognize_google(audio)

                    threading.Thread(target=callback, args=(text, None)).start()
