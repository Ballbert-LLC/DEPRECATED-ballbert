import importlib
import inspect
import json
import multiprocessing
import os
import shutil
import sqlite3
import sys
import threading
import uuid
import asyncio
import websockets


import openai
import yaml
from git import Repo

from Config import Config

from ..ASR import ASR
from ..Classes import Response
from ..Decorators import paramRegistrar, reg
from ..Logging import log_line
from ..Memory import Weaviate
from ..MessageHandler import MessageHandler
from ..TTS import TTS
from ..Utils import generate_system_message
from ..Voice import Voice
from .SkillMangager import SkillMangager

repos_path = f"{os.path.abspath(os.getcwd())}/Skills"

config = Config()

openai.api_key = config["OPENAI_API_KEY"]


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

        self.messages = [generate_system_message()]
        self.pm = pm
        self.installed_skills = dict()
        self.action_dict = dict()
        self.skill_manager = SkillMangager()
        self.voice = None
        self.tts = None
        self.speak_mode = False
        self.current_callback = None

    async def voice_to_text_chat(self):
        self.voice = Voice()

        async def callback(res, err):
            if err:
                print(err)
            elif res:
                res: str = res
                async for item in self._text_gpt_response(res):
                    print(item, end="", flush=True)
                print()

        self.voice.start(callback)

    async def sentance_gen(self, res):
        buffer = ""
        index = 0
        async for content in self._text_gpt_response(res):
            for char in content:
                if char in [".", "!", "?"]:
                    buffer += char
                    yield (buffer, index)
                    index += 1
                    buffer = ""
                else:
                    buffer += char

    async def voice_to_voice_chat(self):
        self.tts = TTS()
        self.voice = Voice()

        async def callback(res, err):
            gen = self.sentance_gen(res)

            await self.tts.speak_gen(gen)

        self.voice.start(callback)

    async def text_chat(self):
        while True:
            question = input("Q: ")
            async for item in self._text_gpt_response(question):
                print(item, end="", flush=True)
            print()

    async def text_to_voice(self):
        self.tts = TTS()
        while True:
            question = input("Q: ")
            gen = self.sentance_gen(question)

            self.tts.speak_gen(gen)

    async def _text_gpt_response(self, to_gpt):
        message_handler = MessageHandler(self, to_gpt)

        async for chunk in message_handler.handle_message():
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
