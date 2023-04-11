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
        self.messages = [
            {"role": "system",
                "content": f"Your name is hal a voice assistant. When provided with a action from the list {str(actions)} output it as a json with just the action and params and start with the letters 'JS:'. Do not propt for optional commands or use deaults. Respond exteamly briefly and consisely. If you cannot find an action respond normaly. Messages starting with Response: are from the backend. You should try to answer the Question part in the messages as you normally would but with the data from the backend. No answers should be prefixed"},
            {"role": "user", "content": "wait for 1 day"},
            {"role": "assistant",
                "content": 'JS:[{"action": "wait", "params": {"seconds": 86,400}}]'},
            {"role": "user", "content": "Response: {status-code: 200} Question: wait for 1 day"},
            {"role": "assistant",
                "content": 'Waited for 1 day'},
        ]
        self.model = "gpt-3.5-turbo"
        self.stream = True

    def ask(self, message):
        self.messages.append({"role": "user", "content": message})
        res = openai.ChatCompletion.create(
            stream=self.stream,
            model=self.model,
            messages=self.messages
        )
        collected_messages = []
        for chunk in res:
            if "content" in chunk["choices"][0]["delta"]:
                collected_messages.append(
                    chunk["choices"][0]["delta"]["content"])
            if chunk["choices"][0]["finish_reason"]:
                self.messages.append(
                    {"role": "assistant", "content": "".join(collected_messages)})
            yield chunk
