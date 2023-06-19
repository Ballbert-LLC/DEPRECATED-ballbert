import importlib
import inspect
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
from ..Utils import convert_dict_to_lower, execute_response, get_action_from_response
from ..Logging import log_line
from ..Wake_Word import Wake_Word

from git import Repo

MODEL = "gpt-3.5-turbo-0613"

repos_path = f"{os.path.abspath(os.getcwd())}/Skills"

config = Config()

openai.api_key = config.open_ai_api_key


class Assistant:
    _instance = None

    def __new__(cls, *args, **kwargs):
        print(cls._instance)
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
            log_line(f"Q: {question}")
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
                log_line(f"Q: {question}")
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

    def _handle_json(self, the_json):
        print(the_json)

    def _text_gpt_response(self, to_gpt):
        self.messages.append({"role": "user", "content": to_gpt})

        res = openai.ChatCompletion.create(
            model=MODEL,
            messages=self.messages,
            temperature=0,
            # functions=functions,
            stream=True,
        )

        function_name = ""
        arguments = ""

        full_message = ""

        for item in res:
            delta = item["choices"][0]["delta"]

            # check for end
            if delta == {}:
                if function_name:
                    self.messages.append(
                        {
                            "role": "function_call",
                            "name": function_name,
                            "arguments": arguments,
                        }
                    )
                else:
                    self.messages.append({"role": "assistant", "content": full_message})

            if "function_call" in delta:
                function_call = delta["function_call"]
                if "name" in function_call:
                    function_name = function_call["name"]
                elif "arguments" in function_call:
                    arguments += function_call["arguments"]
            elif "content" in delta:
                full_message += delta["content"]
                yield delta["content"]

        print(function_name, arguments)
        yield "."

    def text_chat(self):
        while True:
            question = input("Q: ")
            log_line(f"Q: {question}")
            for item in self._text_gpt_response(question):
                print(item, end="", flush=True)
            print()

    def send_response(response: Response):
        print(response)

    def add_skill_from_url(self, url):
        self.skill_manager.add_skill_from_url(self, url)

    def remove_skill(self, skill_name):
        self.skill_manager.remove_skill(skill_name, self)

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

        # Execute a SELECT query on the installedSkills table
        cur.execute("SELECT * FROM installedSkills")
        installed_skills_data = cur.fetchall()

        for item in installed_skills_data:
            print(item[0])
            assistant.skill_manager.add_skill(assistant, item[0])

        con.commit()

        con.close()

        return assistant

    else:
        return assistant
