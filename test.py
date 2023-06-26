import json
import os

os.environ["debug_mode"] = "True"

from Hal.Assistant.Assistant import initialize_assistant
from Hal.Utils.utils import rmtree_hard
from setup import setup

setup()

assistant_instance = initialize_assistant()

assistant_instance.skill_manager.add_skill_from_url(
    assistant_instance, "https://github.com/seesi8/HalAdvancedMath.git"
)


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


print(serialize_dictionary(assistant_instance.installed_skills))
