import importlib
import inspect
import os
import shutil
import sqlite3
import sys
import threading
import uuid

import yaml
import multiprocessing

from .SkillMangager import SkillMangager
from ..ASR import ASR
from ..Chat_Gpt import Chat_Gpt
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

repos_path = f"{os.path.abspath(os.getcwd())}/Skills"

config = Config()


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

        self.pm = pm
        self.installed_skills = dict()
        self.action_dict = dict()
        self.chatbot = Chat_Gpt(config.name, api_key=config.open_ai_api_key)
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
        response = self.chatbot.ask(to_gpt)

        total_message = ""

        spoken_message = ""

        backend_message = ""

        should_add_to_backend = False

        currently_speaking = ""

        speech_control = 0

        for chunk in response:
            if "content" in chunk["choices"][0]["delta"]:
                content = chunk["choices"][0]["delta"]["content"]
                total_message += content
                if "🖥" in content or should_add_to_backend:
                    backend_message += content
                    should_add_to_backend = True
                else:
                    spoken_message += content
                    currently_speaking += content
                if should_add_to_backend == False:
                    yield content
                # check for begining
                if (
                    '"speech": ' in total_message
                    and '"' in content
                    and speech_control != -1
                ):
                    speech_control += 1
                # check for content
                if speech_control > 0:
                    currently_speaking += content
                    spoken_message += content
                # check for end
                if speech_control > 0 and '",' in spoken_message:
                    speech_control = -1
                # fix it
                if '"' in spoken_message:
                    spoken_message = spoken_message.replace(' "', "")
                    currently_speaking = currently_speaking.replace(' "', "")
                    spoken_message = spoken_message.replace('"', "")
                    currently_speaking = currently_speaking.replace('"', "")
                # fic it
                if '",' in spoken_message:
                    spoken_message = spoken_message.replace('",', "")
                # buffer speech
                if speech_control == 1:
                    yield currently_speaking
                    currently_speaking = ""
        log_line(f"A: {total_message}")

        # add finish
        yield "."

        if "🖥️" in backend_message:
            functions = {
                key: value["function"] for key, value in self.action_dict.items()
            }
            backend_res = execute_response(actions=functions, response=backend_message)
            action = get_action_from_response(backend_message)

            response_message = create_response_message(action, backend_res)

            if action in self.action_dict:
                log_line(f"S: {response_message}")

                self._text_gpt_response(response_message)

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
            assistant.skill_manager.add_skill(assistant, item[0])
        return assistant
    else:
        return assistant
