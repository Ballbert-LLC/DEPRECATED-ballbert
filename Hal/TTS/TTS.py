import time
import simpleaudio as sa
from multiprocessing.managers import BaseManager
from multiprocessing import Process
from random import randint
from time import sleep
import io
import os
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.playback import play
import multiprocessing

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./hal-assistant-383917-8b11225b2c1a.json"

class CustomManager(BaseManager):
    # nothing
    pass

class UnfixedList(list):
    def __init__(self, iter=[], *args, **kwargs):
        super(UnfixedList, self).__init__(iter)

    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([None] * (index - len(self) + 1))
        super(UnfixedList, self).__setitem__(index, value)

    def set(self, index, value):
        if index >= len(self):
            self.extend([None] * (index - len(self) + 1))
        super(UnfixedList, self).__setitem__(index, value)

    def pop(self, index=None):
        if index:
            self[index] = None
        for item in self:
            if item != None:
                item = None
                break

    def get_list(self):
        return list(self)

    def available_packets(self):
        index = 0
        while True:
            while index >= len(self) or self[index] is None:
                time.sleep(0.1)  # Delay for 0.1 seconds
            yield self[index]
            index += 1

    def get(self, index):
        try:
            return self[index]
        except IndexError:
            return None

    def __len__(self) -> int:
        count = 0
        for item in self:
            if item != None:
                count += 1

        return count

    def isEmpty(self) -> bool:
        return len(self) == 0


class TTS():
    def __init__(self) -> None:
        self.sentances = UnfixedList()
        CustomManager.register('TTS', TTS)

    def add_sentance(self, index, text):
        self.sentances.set(index, text)

    def proccess_text(self, text: str):
        client = texttospeech.TextToSpeechClient()

        input_text = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz = 24000
        )

        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config
        )

        audio_bytes = response.audio_content
        return audio_bytes

    def _play_text(self, audio):
        #have to cut off begining to prevent weird popping
        start_after = 46
        # Create a simpleaudio WaveObject from the audio content
        wave_obj = sa.WaveObject(audio[start_after:], num_channels=1, bytes_per_sample=2, sample_rate=24000)
        
        # Play the audio
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def get_sentances(self):
        return self.sentances

    def start_loop(self):
        index = 0
        while True:
            while self.sentances.get(index) is None:
                time.sleep(0.1)  # Delay for 0.1 seconds
            if self.sentances.get(index) == "%EXIT%":
                break
            self._play_text(self.sentances.get(index))
            self.sentances.pop()
            index += 1
        return

    def add_exit_code(self):
        self.sentances.append("%EXIT%")
    def speak_gen(self, gen):
        with CustomManager() as manager:
            ttsManger = manager.TTS()

            process2 = Process(target=ttsManger.start_loop, args=())

            process2.start()
            

            for item in gen:
                audio = ttsManger.proccess_text(item[0])
                ttsManger.add_sentance(item[1], audio)

            ttsManger.add_exit_code()

            while True:
                if not process2.is_alive():
                    process2.join()
                    break
                time.sleep(.1) 

