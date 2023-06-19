import unittest
import ast
import json
import sys
import os

working_dir = os.path.abspath("./")

sys.path.append(working_dir)


from Hal import assistant, initialize_assistant
from setup import setup
from Config import Config

config = Config()

is_debug = config.debug_mode

assistant_instance = initialize_assistant()


def remove_uuid(dictionary):
    if isinstance(dictionary, dict):
        for key in list(dictionary.keys()):
            if key == "uuid":
                dictionary.pop(key)
            else:
                remove_uuid(dictionary[key])
    elif isinstance(dictionary, list):
        for item in dictionary:
            remove_uuid(item)


def serialize_dictionary(dictionary):
    remove_uuid(dictionary)

    class Encoder(json.JSONEncoder):
        def default(self, obj):
            if callable(obj):  # Check if the object is a function
                return obj.__name__  # Serialize the function as its name
            elif hasattr(obj, "__dict__"):  # Check if the object is a class instance
                return obj.__dict__  # Serialize the class instance as its dictionary
            return super().default(obj)

    serialized = json.dumps(dictionary, cls=Encoder, indent=4)
    return serialized


action_dict = serialize_dictionary(assistant_instance.action_dict)
installed_skills = serialize_dictionary(assistant_instance.installed_skills)


def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


# Provide the path to your JSON file
correct_installed_skills_path = os.path.abspath(
    "./tests/Installing_Skills/Correct_Skills.json"
)
correct_actions_dict_path = os.path.abspath(
    "./tests/Installing_Skills/Correct_Actions.json"
)


# Call the function to read the JSON file
correct_installed_skills = serialize_dictionary(
    read_json_file(correct_installed_skills_path)
)

correct_actions_dict = serialize_dictionary(read_json_file(correct_actions_dict_path))


def highlight_diff(dict1_str, dict2_str):
    if isinstance(dict1_str, str):
        dict1 = json.loads(dict1_str)
    else:
        dict1 = dict1_str

    if isinstance(dict2_str, str):
        dict2 = json.loads(dict2_str)
    else:
        dict2 = dict2_str

    all_keys = set(dict1.keys()).union(dict2.keys())

    for key in all_keys:
        if isinstance(dict1.get(key), dict) and isinstance(dict2.get(key), dict):
            highlight_diff(
                dict1[key], dict2[key]
            )  # Recursively compare nested dictionaries
        elif dict1.get(key) != dict2.get(key):
            value1 = dict1.get(key)
            value2 = dict2.get(key)
            print(f"Key '{key}':")
            print(f"    First dict value: {value1}")
            print(f"    Second dict value: {value2}")
            print("")


os.environ["DEBUG_MODE"] = str(is_debug)

print(
    (
        "\033[92m"
        if correct_actions_dict == action_dict and action_dict == correct_actions_dict
        else "\033[91m"
    )
    + "Without Setup: "
    + (
        "passed"
        if correct_actions_dict == action_dict and action_dict == correct_actions_dict
        else "failed"
    )
)
