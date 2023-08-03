import asyncio
import json
import os
import platform
import pvporcupine
import pyaudio
import speech_recognition as sr
from pvrecorder import PvRecorder
import threading

import websockets
from Config import Config
import numpy as np
import soxr

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

    def start(self, callback):
        # the mics sample rate is 44100
        mic = sr.Microphone(device_index=1)
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 5000

        def make_callback(text, err):
            try:
                asyncio.run(callback(text, err))
            except Exception as e:
                print(e)

        def send_color(color):
            async def send_color_to_ws(color):
                async with websockets.connect("ws://localhost:8765") as websocket:
                    json_data = json.dumps({"type": "color", "color": color})

                    await websocket.send(json_data)

            def send_color_factory(color):
                try:
                    asyncio.run(send_color_to_ws(color))
                except Exception as e:
                    print(e)

            t = threading.Thread(target=send_color_factory, args=(color,))
            t.start()
            return t

        send_color("grey")
        with mic as source:
            while True:
                if os.path.exists("./UPDATE"):
                    break
                # Start recording
                audio_frames = source.stream.read(1410)

                np_audio_data = np.frombuffer(audio_frames, dtype=np.int16)

                np_audio_data = soxr.resample(np_audio_data, 44100, 16000)

                keyword_index = self.porcupine.process(np_audio_data)
                if keyword_index >= 0:
                    send_color("blue")
                    print("Keyowrd Detected")
                    audio = recognizer.listen(
                        source=source,
                    )
                    try:
                        text = recognizer.recognize_google(audio)
                        print("text", text)
                        threading.Thread(
                            target=make_callback, args=(text, None)
                        ).start()

                    except Exception as e:
                        print(e)
                        threading.Thread(target=make_callback, args=("", e)).start()
