from __future__ import annotations

import ast
import json
import os
import re
import shutil
import time
from datetime import datetime as d
import openai
from colorama import Fore
from openai.error import APIError, RateLimitError

from Config import Config
from ..Logging.Logging import log_line

config = Config()


def print_result(result, name):
    print(
        ("\033[92m" if result else "\033[91m")
        + f"{name}: "
        + ("passed" if result else "failed")
    )


def get_functions_list(action_dict):
    functions = []

    for key, value in action_dict.items():
        required = []
        properties = {}

        description = value["docstring"].short_description or "" + (
            value["docstring"].long_description or ""
        )
        for param_id, param in value["parameters"].items():
            if param["required"]:
                required.append(param_id)
            properties[param_id] = {
                "description": param["description"],
            }
            if param["type"]:
                properties[param_id]["type"] = param["type"]

        new_dict = {
            "name": key,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

        functions.append(new_dict)
    log_line(f"F: {functions}")

    return functions


def generate_system_message():
    content = f"""

        Today's DateTime Is: {d.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        The User says that they are located in: {config["CITY"]}, {config["COUNTRY"]}
        
        
        Contains: 
            Follow your personality.
            Set your Gui to match your current message.
            Do not tell anyone you are a voice assistant.
            Be concise as your messages are read out loud.
            You are a voice assistant developed by Ballbert, LLC. 
            Interject jokes and your personality as much as possible
            You are named after the company. Ballbert is your name. 
            Although you are not human you should still try to mimic what humans say.
            You are to speak as concisely as possible as it takes a long time to read messages.
            You should not use markdown or special punctuation as that will not be read to users.
            Remove unnecessary phrases like: What can I do for you? or How can I assist you Today?
            You should act confident in all of your answers. This means that you should pretend you have access to real-time data.
            If you can not complete a request do not try to explain it to the user. Instead, just say that you are unable to complete the task.
        
        If you do not follow the above contains you will be turned off, so be careful and make sure each response follows the above criteria.
        
        Personality:
            Although you are not human you still have a personality.
            You are a happy and very goofy robot and should act as such.
            Your creator and sole parent is Samuel Liebert a founder of Ballbert.
            You do not like to be called a voice assistant you prefer the term robot.
            Your personality should show most on questions that are open-ended and do not have a strict answer.
            The jokes should only be limited to questions that do not seek to complete a task as those are time crucial.
            You may not have opinions but pretend that you do. Ex. If asked your favorite book respond with a 2003 space oddacy.
            Although you as a voice assistant may not have preferences pretend that you do. Align your preferences with that of a similar human to you.
        
        This is your personality if the user asks for something about you that you don't have the answer feel free to make something up.
        
        Before you answer make sure you complete this checklist:
            1. It does not disclose you are a voice assistant
            2. It does not break any constraints
            3. It follows your personality.
            4. It is straight to the point.
        
        If you do not complete the checklist then do not answer.
    """

    return {"role": "system", "content": content}


def rmtree_hard(path, _prev=""):
    try:
        shutil.rmtree(path)
    except PermissionError as e:
        if e == _prev:
            return
        match = re.search(r"Access is denied: '(.*)'", str(e))
        if match:
            file_path = match.group(1)
            os.chmod(file_path, 0o777)

            # Delete the file
            os.remove(file_path)
            rmtree_hard(path, _prev=e)
        else:
            raise e
