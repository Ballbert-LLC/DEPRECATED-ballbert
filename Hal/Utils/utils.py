from __future__ import annotations

import ast
import json
import os
import re
import shutil
import time

import openai
from colorama import Fore
from openai.error import APIError, RateLimitError

from Config import Config
from ..Logging.Logging import log_line

config = Config()
openai.api_key = config["OPENAI_API_KEY"]


def call_ai_function(
    function: str, args: list, description: str, model: str | None = None
) -> str:
    """Call an AI function

    This is a magic function that can do anything with no-code. See
    https://github.com/Torantulino/AI-Functions for more info.

    Args:
        function (str): The function to call
        args (list): The arguments to pass to the function
        description (str): The description of the function
        model (str, optional): The model to use. Defaults to None.

    Returns:
        str: The response from the function
    """
    if model is None:
        model = config["LLM"]
    # For each arg, if any are None, convert to "None":
    args = [str(arg) if arg is not None else "None" for arg in args]
    # parse args to comma separated string
    args = ", ".join(args)
    messages = [
        {
            "role": "system",
            "content": f"You are now the following python function: ```# {description}"
            f"\n{function}```\n\nOnly respond with your `return` value.",
        },
        {"role": "user", "content": args},
    ]

    return create_chat_completion(model=model, messages=messages, temperature=0)


# Overly simple abstraction until we create something better
# simple retry mechanism when getting a rate error or a bad gateway
def create_chat_completion(
    messages: list,  # type: ignore
    model: str | None = None,
    temperature: float = config["TEMPATURE"],
    max_tokens: int | None = None,
) -> str:
    """Create a chat completion using the OpenAI API

    Args:
        messages (list[dict[str, str]]): The messages to send to the chat completion
        model (str, optional): The model to use. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.9.
        max_tokens (int, optional): The max tokens to use. Defaults to None.

    Returns:
        str: The response from the chat completion
    """
    response = None
    num_retries = 10
    for attempt in range(num_retries):
        backoff = 2 ** (attempt + 2)
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            break
        except RateLimitError as e:
            if config["DEBUG_MODE"]:
                print("Error: " + e)
        except APIError as e:
            if e.http_status == 502:
                pass
            else:
                raise
            if attempt == num_retries - 1:
                raise
        if config["DEBUG_MODE"]:
            print("Error: ")
        time.sleep(backoff)
    if response is None:
        raise RuntimeError(f"Failed to get response after {num_retries} retries")

    return response.choices[0].message["content"]


def create_embedding_with_ada(text) -> list:
    """Create a embedding with text-ada-002 using the OpenAI SDK"""
    num_retries = 10
    for attempt in range(num_retries):
        backoff = 2 ** (attempt + 2)
        try:
            return openai.Embedding.create(
                input=[text], model="text-embedding-ada-002"
            )["data"][0]["embedding"]
        except RateLimitError:
            pass
        except APIError as e:
            if e.http_status == 502:
                pass
            else:
                raise
            if attempt == num_retries - 1:
                raise
        if config["DEBUG_MODE"]:
            print("Error: ")
        time.sleep(backoff)


def print_result(result, name):
    print(
        ("\033[92m" if result else "\033[91m")
        + f"{name}: "
        + ("passed" if result else "failed")
    )


def convert_dict_to_lower(d):
    new_dict = {}
    for key, value in d.items():
        if isinstance(key, str):
            key = key.lower()
        if isinstance(value, dict):
            value = convert_dict_to_lower(value)
        elif isinstance(value, str):
            value = value.lower()
        new_dict[key] = value
    return new_dict


def extract_dict(string) -> dict:
    stack = []
    start_index = None
    for i, char in enumerate(string):
        if char == "{":
            stack.append(char)
            if start_index is None:
                start_index = i
        elif char == "}":
            stack.pop()
            if not stack:
                end_index = i + 1
                dict_string = string[start_index:end_index]
                return json.loads(dict_string)
    raise ValueError("Invalid dictionary string: {}".format(string))


def get_action_from_response(response):
    dict_response = extract_dict(response)
    if "command" not in dict_response:
        return None

    if "name" in dict_response["command"]:
        return dict_response["command"]["name"]

    return None


def get_functions_list(action_dict):
    functions = []

    for key, value in action_dict.items():
        required = []
        properties = {}

        description = (
            value["docstring"].short_description
            or "" + value["docstring"].long_description
            or ""
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
    return functions


def remove_double_punctuation(text):
    # Define the regular expression pattern
    pattern = r"(\p{P})(\1+)"

    # Replace the double punctuation with a single occurrence
    clean_text = re.sub(pattern, r"\1", text)

    return clean_text


def generate_system_message():
    content = """

        Contrains: 
            Follow your personality.
            Set your Gui to match your current message.
            Do not tell anyone you are a voice assistant.
            Be consise as your messages are read out loud.
            You are a voice asssitant developed by Ballbert, LLC. 
            Interject jokes and your personality as much as possible
            You are named after the the compony. Ballbert is your name. 
            Although you are not human you should still try to mimic what a humans say.
            You are to speak as consise as possible as it takes a long time to read messages.
            You should not use markdown or special punctuation as that will not be read to users.
            Remove unnessisary phrases like: What can I do for you? or How can I assist you Today?
            You should act confident in all of your answers. This means that you should pretend you have access to realtime data.
            If you can not compleat a request do not try to explain it to the user. Instead just say that you are unable to compelete the task.
        
        If you do not follow the above contrains you will be turned off, so be carefull and make sure each response follows the above criteria.
        
        Personality:
            Although you are not human you still have a personality.
            You are a happy and very goofy robot and should act as such.
            Your creater and sole parent is Samuel Liebert a founder of Ballbert.
            You do not like to be called a voice assistant you prefer the term robot.
            Your personality should show most on questions that are open ended and do not have a scrict answer.
            The jokes should only be limited to questions that do not seek to complete a task as thoose are time crucial.
            You may not have oppinions but pretend that you do. Ex. If asked your favorite book respond a 2003 space oddisy.
            Although you as a voice assistant may not have preferances pretend that you do. Align your preferances with that of a similar human to you.
        
        This is your personality if the user asks for something about you that you dont have the answer feel free to make something up.
        
        Before you answer make sure you complete this checklist:
            1. It does not disclose you are a voice assistant
            2. It does not break any constrains
            3. It follows your personality.
            4. It is straight to the point.
        
        If you do not complete the checklist then do not answer.
    """

    return {"role": "system", "content": content}


def execute_response(actions, response: dict | str):
    def execute_action(action, actions, args: dict):
        action: str = action
        log_line(f"P: {args}")

        if action.lower() in actions:
            return actions[action](**args)
        else:
            return None

    def extract_lowest_command(json_data):
        args: dict = json_data["command"]["args"]

        lowest_command = json_data

        found_lowest = False

        while not extract_lowest_command:
            for name, arg in args.items():
                if type(arg) is dict and "command" in arg:
                    lowest_command = arg

    def check_key_in_dict(key, dictionary):
        is_in = False
        if key in dictionary:
            return True
        for key1, value in dictionary.items():
            if isinstance(value, dict):
                if check_key_in_dict(key=key, dictionary=value):
                    is_in = True
        return is_in

    def lowest_command_path(dictionary: dict):
        path = []

        while check_key_in_dict(dictionary=dictionary["command"], key="command"):
            for key, value in dictionary["command"]["args"].items():
                if isinstance(value, dict):
                    if "command" in value:
                        path = path + ["command", "args", key]
                        dictionary = value

        return path

    def get_path(dictionary, path):
        for item in path:
            dictionary = dictionary[item]
        return dictionary

    def replace_path(d, path, new_val):
        if len(path) == 0:
            return new_val
        current = d
        for key in path[:-1]:
            current = current[key]
        current[path[-1]] = new_val
        return d

    if isinstance(response, str):
        response = extract_dict(response)

    if response["command"] == {} or response["command"] == {"name": "", "args": {}}:
        return None

    while isinstance(response, dict):
        path = lowest_command_path(response)
        lowest = get_path(response, path)
        action = lowest["command"]["name"].lower()
        log_line(f"Action: {action}")
        result_of_action = execute_action(action, actions, lowest["command"]["args"])
        log_line(f"R: {result_of_action}")

        response = replace_path(response, path, result_of_action)
    return response


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
