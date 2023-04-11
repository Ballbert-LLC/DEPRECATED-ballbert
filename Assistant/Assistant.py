import importlib
import inspect

from Chat_Gpt import Chat_Gpt
from Classes import Response
from Decorators import paramRegistrar, reg


class Assistant:
    def __init__(self, skills=[]):

        for skill in skills:
            importlib.import_module(skill)

        # full set of actions with function and paramiters
        actions = {skill_id: {"parameters": {}}
                   for skill_id, func in reg.all.items()}

        # get all of the action functions from the decorator
        action_functions: dict[str, function] = reg.all

        # get all of the paramiters from the decorator
        parameters = set()

        for skill_id, func in action_functions.items():
            _parameters = inspect.signature(func).parameters

            # add paramiters to actions
            actions[skill_id]["parameters"] = set(
                argument for argument in _parameters)

            # back to working with paramiters
            _parameters = set(
                f"{skill_id}.{argument}" for argument in _parameters)
            parameters = parameters.union(_parameters)

        # get all of the possible paramiters
        possible_paramiters = dict()

        for skill_id, func in paramRegistrar.all.items():
            possible_paramiters[skill_id] = []
            for item in func():
                possible_paramiters[skill_id].append(item)

        # chatbot
        api_key = "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"

        self.action_functions = action_functions
        self.parameters = parameters
        self.possible_paramiters = possible_paramiters
        self.actions = actions
        self.chatbot = Chat_Gpt("Hal", api_key=api_key, actions=self.actions)

    def text_chat(self):
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
                    if is_json != None:
                        if buffer and is_json == False:
                            print(buffer, end="", flush=True)
                            buffer = ""
                        print(content, end="", flush=True)
                    else:
                        buffer += content

            print(is_json)

    def send_response(response: Response):
        print(response)
