import pyttsx3

test = "the quick brown fox"


class TTS:
    def __init__(self, lang: str, voice_id="com.apple.speech.synthesis.voice.Alex"):
        engine = pyttsx3.init()
        engine.setProperty('voice', voice_id)

        self.engine = engine

    def get_voices():
        voices = self.engine.getProperty('voices')

        engine.say(test)
        engine.runAndWait()
        for voice in voices:
            if "en_US" in voice.languages:
                print("Voice:")
                print(" - ID: %s" % voice.id)
                print(" - Name: %s" % voice.name)
                print(" - Languages: %s" % voice.languages)
                print(" - Gender: %s" % voice.gender)
                print(" - Age: %s" % voice.age)
