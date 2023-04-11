import time

from Classes import Response
from Decorators import reg


class Wait_Skill:
    @reg
    def wait_seconds(seconds):
        try:
            time.sleep(seconds)
            response = Response(
                data={"status-code": 200, "time-weighted": seconds}, suceeded=True)
        except:
            response = Response(suceeded=False)
        return response
