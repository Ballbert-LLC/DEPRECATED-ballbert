import datetime
from uuid import uuid4

from ..Classes import Action, Response


class Instruction:

    def __init__(self, actions: list[Action], utterance):
        self.time_started = datetime.datetime.now()
        self.time_finished = None
        self.actions = actions.copy()
        self.utterance = utterance
        self.current_action = None
        self.previous_actions = []
        self.uuid = uuid4()
        self.future_actions = actions.copy()
        self.responses: list[Response] = []

    def pause(self):
        self.current_action
        self.paused = True

    def next(self):
        # add to previous
        if self.current_action is not None:
            self.previous_actions.append(self.current_action)
        # set next action
        self.current_action = self.future_actions[0]
        # remove new current action from future action
        self.future_actions.remove(self.current_action)
        # call current action
        response: Response = self.current_action.execute()
        response.action = self.current_action.action_id
        response.original_message = self.utterance

        return response

    def run_actions(self):
        for action in self.actions:
            self.responses.append(self.next())
        return self.responses
