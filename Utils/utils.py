from __future__ import annotations

import ast
import json
import time

import openai
from colorama import Fore
from openai.error import APIError, RateLimitError

from Config import Config
from Logging.Logging import log_line

config = Config()
openai.api_key = config.open_ai_api_key


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
        model = config.llm
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
    temperature: float = config.tempature,
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
        except RateLimitError:
            if config.debug_mode:
                print(
                    "Error: "
                )
        except APIError as e:
            if e.http_status == 502:
                pass
            else:
                raise
            if attempt == num_retries - 1:
                raise
        if config.debug_mode:
            print(
                "Error: "
            )
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
        if config.debug_mode:
            print(
                "Error: "
            )
        time.sleep(backoff)
        
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
        if char == '{':
            stack.append(char)
            if start_index is None:
                start_index = i
        elif char == '}':
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

    if response["command"] == {} or response["command"] == {
        "name": "",
        "args": {}
    }:
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
        
        