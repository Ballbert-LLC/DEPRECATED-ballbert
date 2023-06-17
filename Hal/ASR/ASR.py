# import library

import speech_recognition as sr

# Initialize recognizer class (for recognizing the speech)


class ASR:
    def __init__(self) -> None:
        self.r = sr.Recognizer()
        self.r.pause_threshold = 1

    def get_speach(self):

        # Reading Microphone as source
        # listening the speech and store in audio_text variable

        with sr.Microphone() as source:
            # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling

            try:
                # using google speech recognition
                audio_text = self.r.listen(source, timeout=5)
                print("dl")

                text = self.r.recognize_google(audio_text)
                print("dr")
                return text
            except Exception as e:
                return ""
