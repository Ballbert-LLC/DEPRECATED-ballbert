import json

import openai


class Chat_Gpt:
    """creates a new chatbot object

    Args:
        name (str): name for chatbot
        actions (str): actions for the chatbot
        possible_parmas (dict): possible params it can have

    Returns:
        (Generator[Any | list | dict, None, None] | Any | list | dict): response of chat completion
    """

    def __init__(self, name: str, api_key, actions) -> None:
        openai.api_key = api_key
        self.messages = []
        self.model = "gpt-3.5-turbo"
        self.stream = True
        
    def _ask_gpt_from_messages(self, messages):
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream = True
        )
    
    def ask(self, user_input):
        from PromptGenerator import chat_with_ai, create_chat_message
        mpg = chat_with_ai(user_input, self.messages, 4000)

        self.messages.append(create_chat_message(role="user", content=user_input))
        
        message = ""
        
        for chunk in self._ask_gpt_from_messages(mpg):
            if "content" in chunk["choices"][0]["delta"]:
                message += chunk["choices"][0]["delta"]["content"]
            if chunk["choices"][0]["finish_reason"]:
                self.messages.append(create_chat_message(role="assistant", content=message))
            yield chunk
