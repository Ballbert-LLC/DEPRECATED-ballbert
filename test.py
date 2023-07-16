def start(self, callback):
    # Start recording
    self.recorder.start()
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 3000

    while True:
        # Read PCM audio data
        audio_frames = self.recorder.read()

        # Process audio with Porcupine
        keyword_index = self.porcupine.process(audio_frames)

        if keyword_index >= 0:
            print("Keyword detected")

            self.recorder.stop()
            print(config["SR_MIC"], type(config["SR_MIC"]))
            with sr.Microphone(device_index=1) as source:
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
                    print(e, "request error occurred when trying to transcribe audio")
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
