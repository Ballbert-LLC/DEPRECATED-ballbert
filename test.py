from Hal.Voice import Voice

voice = Voice()


def sample_callback(text, _):
    print(text)


voice.test(sample_callback)
