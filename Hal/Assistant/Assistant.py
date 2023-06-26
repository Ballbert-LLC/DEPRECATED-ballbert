import importlib
import inspect
import json
import os
import shutil
import sqlite3
import sys
import threading
import uuid
import openai

import yaml
import multiprocessing

from .SkillMangager import SkillMangager
from ..ASR import ASR
from ..Classes import Response
from Config import Config
from ..Decorators import paramRegistrar, reg
from ..Memory import Weaviate
from ..PromptGenerator import create_response_message
from ..TTS import say_phrase, say_phrase_in_process, stop_saying
from ..Logging import log_line
from ..Wake_Word import Wake_Word
from ..MessageHandler import MessageHandler

from git import Repo


repos_path = f"{os.path.abspath(os.getcwd())}/Skills"

config = Config()

openai.api_key = config.open_ai_api_key


class Assistant:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # pinecone memory
        pm = None
        pm = Weaviate()

        self.messages = []
        self.pm = pm
        self.installed_skills = dict()
        self.action_dict = dict()
        self.skill_manager = SkillMangager()
        self.asr = ASR()
        self.speak_mode = False
        self.current_callback = None

    def text_to_voice_chat(self):
        buffer = ""
        while True:
            question = input("Q: ")
            for item in self._text_gpt_response(question):
                buffer += item
                for punctiation in [".", "?", "!", ",", "-", ";", ":"]:
                    if punctiation in buffer:
                        say_phrase(buffer)
                        buffer = ""
                print(item, end="", flush=True)
            print()

    def voice_to_voice_chat(self):
        def handle():
            if self.current_callback != None:
                self.current_callback()

            try:
                buffer = ""

                wake_word.pause()
                question = self.asr.get_speach()
                for item in self._text_gpt_response(question):
                    buffer += item
                    for punctuation in [".", "?", "!", ",", "-", ";", ":"]:
                        if punctuation in buffer:
                            say_phrase_in_process(buffer)
                            buffer = ""
                    print(item, end="", flush=True)
                print()
                wake_word.resume()
            except Exception as e:
                say_phrase_in_process("sorry please try again")
                wake_word.resume()
                log_line(f"Error: {e}")

        wake_word = Wake_Word(callback=handle)

        def run_wake_word():
            wake_word.start()

        wake_word_thread = threading.Thread(target=run_wake_word)
        wake_word_thread.start()

    def text_chat(self):
        while True:
            question = input("Q: ")
            for item in self._text_gpt_response(question):
                print(item, end="", flush=True)
            print()

    def _text_gpt_response(self, to_gpt):
        message_handler = MessageHandler(self, to_gpt)

        for chunk in message_handler.handle_message():
            yield chunk

    def call_function(self, function_id, args=[], kwargs={}):
        return self.action_dict[function_id]["function"](*args, **kwargs)


# Module-level variable to store the shared instance
assistant = None


# Initialization function to create the instance
def initialize_assistant():
    global assistant
    if assistant is None:
        assistant = Assistant()
        con = sqlite3.connect("skills.db")

        cur = con.cursor()
        try:
            # Execute a SELECT query on the installedSkills table
            cur.execute("SELECT * FROM installedSkills")
            installed_skills_data = cur.fetchall()
        except:
            installed_skills_data = []

        for item in installed_skills_data:
            assistant.skill_manager.add_skill(assistant, item[0])

        con.commit()

        con.close()

        return assistant

    else:
        return assistant
