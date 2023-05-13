import datetime
import multiprocessing
from uuid import uuid4


class Action:
    def __init__(self, action_id: str, params: dict) -> None:
        from Hal import assistant
        self.time_started = datetime.datetime.now()
        self.time_finished = None
        self.uuid = uuid4()
        self.action_id = action_id
        self.params = params
        self.function = assistant.action_dict[action_id]["function"]

    def execute(self):
        self.time_finished = datetime.datetime.now()
        return self.function(**self.params)
