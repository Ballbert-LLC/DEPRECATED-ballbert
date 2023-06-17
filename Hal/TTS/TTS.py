import time
import pyttsx3
import multiprocessing

engine = pyttsx3.init()
lang = "en-us"

current_thread = None


def say_phrase(phrase: str):
    engine.say(phrase)
    engine.runAndWait()


def say_phrase_in_process(phrase: str):
    global current_thread
    thread = multiprocessing.Process(target=say_phrase, args=(phrase,))
    thread.daemon = True
    thread.start()
    current_thread = thread


def stop_saying():
    current_thread.kill()
