import speech_recognition as sr


class VoiceTest:
    def test(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone(device_index=1)
        with mic as source:
            audio = recognizer.listen(
                source=source,
            )

        text = recognizer.recognize_google(audio)
        print(text)
