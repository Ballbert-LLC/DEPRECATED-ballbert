import datetime


class Response:
    def __init__(self, suceeded=False, original_message: str = "", action: str = "", data=None,):
        self.time_created = datetime.datetime.now()
        self.original_message = original_message
        self.data = data
        self.suceeded = suceeded
        self.action = action
