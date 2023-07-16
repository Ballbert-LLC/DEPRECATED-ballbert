from Hal.Voice import Voice

voice = Voice()


def callback(text, error):
    print(text)


voice.start(callback=callback)
