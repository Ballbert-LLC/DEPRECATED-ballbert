import json
from typing import Generator
from flask import Response
import openai

from Hal import Assistant
from ..Utils import get_functions_list
from ..Logging import log_line

MODEL = "gpt-3.5-turbo-0613"


class MessageHandler:
    def __init__(self, assistant: Assistant, gpt_response) -> None:
        self.function_name = ""
        self.arguments = ""
        self.full_message = ""
        self.assistant = assistant
        self.gpt_response = gpt_response

    def get_functions(self, message):
        relevant_ids = self.assistant.pm.get_relevant(message)
        relevant_actions = {
            key: self.assistant.action_dict[key]
            for key in relevant_ids
            if key in self.assistant.action_dict
        }
        functions = get_functions_list(relevant_actions)

        return functions

    def add_to_messages(self, message):
        self.assistant.messages.append({"role": "user", "content": message})

    def add_function_to_messages(self, message, function_name):
        self.assistant.messages.append(
            {"role": "function", "name": function_name, "content": str(message)}
        )

    def ask_gpt(self, functions):
        log_line(f"I: {self.assistant.messages[-1]}")

        def run():
            return openai.ChatCompletion.create(
                model=MODEL,
                messages=self.assistant.messages,
                temperature=0,
                functions=functions,
                stream=True,
            )

        while True:
            try:
                return run()
            except Exception as e:
                print(e)
                pass

    def handle_chunk(self, chunk):
        delta = chunk["choices"][0]["delta"]
        # check for end
        if delta == {}:
            if self.function_name:
                self.assistant.messages.append(
                    {
                        "role": "assistant",
                        "function_call": {
                            "arguments": str(self.arguments),
                            "name": str(self.function_name),
                        },
                        "content": "",
                    }
                )

                if self.function_name:
                    self.arguments = json.loads(self.arguments)

                    function_result: Response = self.assistant.action_dict[
                        self.function_name
                    ]["function"](**self.arguments).data

                    log_line(f"FN: {self.function_name}")
                    log_line(f"Arg: {self.arguments}")

                    function_message_handler = MessageHandler(
                        self.assistant, self.gpt_response
                    )

                    return function_message_handler.handle_function(
                        function_result, self.function_name
                    )
            else:
                self.assistant.messages.append(
                    {"role": "assistant", "content": self.full_message}
                )
                log_line(f"A: {self.full_message}")

        if "function_call" in delta:
            function_call = delta["function_call"]
            if "name" in function_call:
                self.function_name = function_call["name"]
            elif "arguments" in function_call:
                self.arguments += function_call["arguments"]
        elif "content" in delta:
            self.full_message += delta["content"]
            return delta["content"]

        return None

    def handle_function(self, message, function_name):
        self.add_function_to_messages(message, function_name)
        functions = self.get_functions(
            f"{self.gpt_response}, {function_name}:{message}"
        )
        current_chunk = ""
        res = self.ask_gpt(functions)
        for chunk in res:
            chunk_result = self.handle_chunk(chunk)
            if isinstance(chunk_result, Generator):
                for item in self.handle_generatior(chunk_result):
                    current_chunk = item
                    yield item
            if chunk_result:
                current_chunk = chunk_result
                yield chunk_result
        
        if isinstance(current_chunk, str):
            if not current_chunk[-1] in ".?!'":
                yield "."

    def handle_generatior(self, generator):
        for item in generator:
            if isinstance(item, Generator):
                for sub_item in self.handle_generatior(item):
                    yield sub_item
            else:
                yield item

    def handle_message(self):
        self.add_to_messages(self.gpt_response)
        functions = self.get_functions(self.gpt_response)
        res = self.ask_gpt(functions)

        current_chunk = ""
        
        for chunk in res:
            chunk_result = self.handle_chunk(chunk)
            if isinstance(chunk_result, Generator):
                for item in self.handle_generatior(chunk_result):
                    current_chunk = item
                    yield item
            elif chunk_result:
                current_chunk = chunk_result
                yield chunk_result
        if isinstance(current_chunk, str):
            if not current_chunk[-1] in ".?!'":
                yield "."
