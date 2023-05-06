import importlib
import inspect
import os
import shutil
import sqlite3
import uuid

import yaml

from .SkillMangager import SkillMangager
from ..ASR import ASR
from ..Chat_Gpt import Chat_Gpt
from ..Classes import Response
from Config import Config
from ..Decorators import paramRegistrar, reg
from ..Memory import Weaviate
from ..PromptGenerator import create_response_message
from ..TTS import TTS
from ..Utils import (convert_dict_to_lower, execute_response,
                     get_action_from_response)
from ..Logging import log_line
from ..Wake_Word import Wake_Word

from git import Repo

repos_path = f"{os.path.abspath(os.getcwd())}/Skills"

config = Config()


class Assistant:
    def __init__(self, skills=[]):

        for skill in skills:
            importlib.import_module(skill)

        # set a action dictionary
        action_dict: dict = reg.all

        # get paramiters from decorator
        for skill_id, item in action_dict.items():
            _parameters = tuple(inspect.signature(
                item["function"]).parameters.items())

            for argument in _parameters:
                _name = argument[0]
                _type = f"<{argument[1].annotation}>" if type(
                    argument[1].annotation) is str else f"<{argument[0]}>"
                action_dict[skill_id]["parameters"] = {_name: _type}

        # get all of the action
        actions: list[tuple] = [(item["name"], item["id"], item["parameters"])
                                for skill_id, item in reg.all.items()]

        # pinecone memory
        pm = None
        pm = Weaviate()

        con = sqlite3.connect("skills.db")

        cur = con.cursor()

        # Execute a SELECT query on the installedSkills table
        cur.execute('SELECT * FROM installedSkills')

        self.pm = pm
        self.installed_skills = list()
        self.actions = actions
        self.action_dict = action_dict
        self.chatbot = Chat_Gpt(
            config.name, api_key=config.open_ai_api_key, actions=self.actions)
        # self.tts = TTS(lang="en-US")
        self.skill_manager = SkillMangager()
        self.tts = None
        self.asr = ASR()
        self.speak_mode = False
        self.action_functions = {key: value["function"]
                                 for key, value in self.action_dict.items()}

        # install skills
        installed_skills_data = cur.fetchall()
        for item in installed_skills_data:
            self.skill_manager.add_skill(self, item[0])

    def text_to_voice_chat(self):
        while True:
            question = input("Q: ")

            response = self.chatbot.ask(question)
            message = ""

            buffer = ""

            json_identifier = "JS:"
            is_json = None

            for i, chunk in enumerate(response):
                if "content" in chunk["choices"][0]["delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    message += content
                    if json_identifier == "" and is_json == None:
                        is_json = True
                    elif is_json == None:
                        for letter in content:
                            if letter in json_identifier and json_identifier.index(letter) == 0:
                                json_identifier = json_identifier.replace(
                                    letter, "", 1)

                            elif json_identifier != "":
                                is_json = False
                    if is_json == False and any(s in config.punctuition for s in content):
                        if buffer:
                            self.tts.say_phrase(buffer + content)
                            buffer = ""
                    else:
                        buffer += content

            file = open("logs.txt", "w")
            file.write("Q: " + question)
            file.write("A: " + message)

    def voice_to_voice_chat(self):
        def callback():
            wake_word.pause()
            line = self.asr.get_line()
            response = self.chatbot.ask(line)
            message = ""

            buffer = ""

            json_identifier = "JS:"
            is_json = None

            for i, chunk in enumerate(response):
                if "content" in chunk["choices"][0]["delta"]:
                    content = chunk["choices"][0]["delta"]["content"]
                    message += content
                    if json_identifier == "" and is_json == None:
                        is_json = True
                    elif is_json == None:
                        for letter in content:
                            if letter in json_identifier and json_identifier.index(letter) == 0:
                                json_identifier = json_identifier.replace(
                                    letter, "", 1)
                            elif json_identifier != "":
                                is_json = False
                    if is_json == False and any(s in config.punctuition for s in content):
                        if buffer:
                            self.tts.say_phrase(buffer + content)
                            buffer = ""
                    else:
                        buffer += content
            if (is_json):
                self._handle_json(message)
            wake_word.resume()

        wake_word = Wake_Word(callback=callback)

        wake_word.start()

    def _handle_json(self, the_json):
        print(the_json)

    def _text_gpt_response(self, to_gpt):

        response = self.chatbot.ask(to_gpt)

        total_message = ""

        spoken_message = ""

        backend_message = ""

        should_add_to_backend = False

        currently_speaking = ""

        speach_control = 0

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
                    print(content, end="", flush=True)
                # check for begining
                if '"speech": ' in total_message and '"' in content and speach_control != -1:
                    speach_control += 1
                # check for content
                if speach_control > 0:
                    currently_speaking += content
                    spoken_message += content
                # check for end
                if speach_control > 0 and '",' in spoken_message:
                    speach_control = -1
                # fix it
                if '"' in spoken_message:
                    spoken_message = spoken_message.replace(' "', '')
                    currently_speaking = currently_speaking.replace(' "', '')
                    spoken_message = spoken_message.replace('"', '')
                    currently_speaking = currently_speaking.replace('"', '')
                # fic it
                if '",' in spoken_message:
                    spoken_message = spoken_message.replace('",', '')
                # buffer speach
                if speach_control == 1:
                    print(currently_speaking, end="", flush=True)
                    currently_speaking = ""
        log_line(f"A: {total_message}")

        if "🖥️" in backend_message:
            backend_res = execute_response(
                actions=self.action_functions, response=backend_message)
            action = get_action_from_response(backend_message)

            response_message = create_response_message(action, backend_res)

            if action in self.action_dict:
                log_line(f"S: {response_message}")

                self._text_gpt_response(response_message)

        print()

    def text_chat(self):
        while True:
            question = input("Q: ")
            log_line(f"Q: {question}")
            self._text_gpt_response(question)

    def send_response(response: Response):
        print(response)

    def add_skill_from_url(self, url):
        self.skill_manager.add_skill_from_url(self, url)

    def remove_skill(self, skill_name):
        self.skill_manager.remove_skill(skill_name, self)
