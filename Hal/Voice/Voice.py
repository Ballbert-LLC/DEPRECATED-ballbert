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
        with sr.Microphone(device_index=1) as source:
            while True:
                # Read PCM audio data
                audio_frames = self.recorder.read()

                # Process audio with Porcupine
                keyword_index = self.porcupine.process(audio_frames)

                if keyword_index >= 0:
                    print("Keyword detected")

                    self.recorder.stop()
                    print(config["SR_MIC"], type(config["SR_MIC"]))
                    try:
                        # Capture speech input
                        audio = recognizer.listen(
                            source,
                        )
                        print("audio", audio, "type", type(audio))
                    except sr.UnknownValueError as e:
                        print("unknown error occurred when trying to transcribe audio")
                        threading.Thread(target=callback, args=("", e)).start()

                    except sr.RequestError as e:
                        print(
                            e, "request error occurred when trying to transcribe audio"
                        )
                        threading.Thread(target=callback, args=("", e)).start()

                    except sr.WaitTimeoutError as e:
                        print(
                            e,
                            "wait timeout error occurred when trying to transcribe audio",
                        )
                        threading.Thread(target=callback, args=("", e)).start()
                    except Exception as e:
                        print(
                            e,
                            "A general error occurred when trying to transcribe audio",
                        )
                        threading.Thread(target=callback, args=("", e)).start()
                    try:
                        # Use Google Speech Recognition to transcribe audio
                        text = recognizer.recognize_google(audio)
                        print("text", text)
                        threading.Thread(target=callback, args=(text, None)).start()
                    except Exception as e:
                        print(e)
                        threading.Thread(target=callback, args=("", e)).start()

                    self.recorder.start()
                else:
                    continue
