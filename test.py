from Hal.Voice import Voice

voice = Voice()


def callback(text):
    print(text)


voice.start(callback=callback)
