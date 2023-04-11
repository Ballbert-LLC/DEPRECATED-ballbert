import pyttsx3

test = "the quick brown fox"

engine = pyttsx3.init()

voices = engine.getProperty('voices')
for voice in voices:
    if "en_US" in voice.languages:
        print("Voice:")
        print(" - ID: %s" % voice.id)
        print(" - Name: %s" % voice.name)
        print(" - Languages: %s" % voice.languages)
        print(" - Gender: %s" % voice.gender)
        print(" - Age: %s" % voice.age)

en_voice_id = "com.apple.speech.synthesis.voice.Alex"
engine.setProperty('voice', en_voice_id)

engine.say(test)
engine.runAndWait()
