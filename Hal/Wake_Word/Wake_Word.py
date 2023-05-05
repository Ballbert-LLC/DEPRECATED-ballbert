import threading

import pvporcupine
from pvrecorder import PvRecorder


class Wake_Word:
    def __init__(self, callback) -> None:
        porcupine = pvporcupine.create(
            access_key="cLByN9IjCzBQOeBiySgZiJRfogghPS0oA28F8M6gnXldykvSDHPLzg==", keywords=["alexa"])
        recoder = PvRecorder(
            device_index=-1, frame_length=porcupine.frame_length)
        self.callback = callback
        self.porcupine = porcupine
        self.recoder = recoder
        self._paused = False

    def _start(self):
        try:
            self.recoder.start()
            while True:
                while self._paused:
                    pass
                pcm = self.recoder.read()
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    pcm = self.recoder.read()
                    while True:
                        keyword_index = self.porcupine.process(pcm)
                        if keyword_index >= 0:
                            pcm = self.recoder.read()
                        else:
                            # Here, you can print out the user's speech
                            self.callback()
                            break
        except KeyboardInterrupt:
            self.recoder.stop()
        finally:
            self.porcupine.delete()
            self.recoder.delete()

    def start(self):
        self._start()

    def resume(self):
        self._paused = False
        self.recoder.start()

    def pause(self):
        self._paused = True
        self.recoder.stop()
