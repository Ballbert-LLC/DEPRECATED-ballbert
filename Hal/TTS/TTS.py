import time

import pyttsx3


class TTS:
    def __init__(self, lang: str, voice_id="com.apple.speech.synthesis.voice.Alex"):
        engine = pyttsx3.init()
        # engine.setProperty('voice', voice_id)
        # engine.setProperty('rate', 500)
        self.lang = lang
        self.engine = engine

    def get_voices(self):
        voices = self.engine.getProperty('voices')

        for voice in voices:
            if self.lang in voice.languages:
                print("Voice:")
                print(" - ID: %s" % voice.id)
                print(" - Name: %s" % voice.name)
                print(" - Languages: %s" % voice.languages)
                print(" - Gender: %s" % voice.gender)
                print(" - Age: %s" % voice.age)

    def say_phrase(self, phrase: str):
        self.engine.say(phrase)
        self.engine.runAndWait()