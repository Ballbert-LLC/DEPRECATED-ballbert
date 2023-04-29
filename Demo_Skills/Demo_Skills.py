import random
import time

from Classes import Response
from Decorators import reg


class Wait_Skill:
    @reg(name="Add")
    def add(a: "number", b: "number"):
        a = int(a)
        b = int(b)
        return Response(suceeded=True, data=a+b)
    @reg(name="Multiply")
    def multiply(a: "number", b: "number"):
        a = int(a)
        b = int(b)
        return Response(suceeded=True, data=a*b)
    @reg(name="Subtract")
    def subtract(a: "number", b: "number"):
        a = int(a)
        b = int(b)
        return Response(suceeded=True, data=a-b)
    @reg(name="Divide")
    def divide(a: "number", b: "number_not_zero"):
        a = int(a)
        b = int(b)
        return Response(suceeded=True, data=a/b)
    @reg(name="Get Random Number")
    def randint(min: "number", max: "number"):
        min = min or 0
        max = max or 10
        min = int(min)
        max = int(max)
        return Response(suceeded=True, data=random.randint(min, max))
    @reg(name="Wait Seconds")
    def wait_seconds(seconds: "seconds"):
        seconds = int(seconds)
        try:
            time.sleep(seconds)
            response = Response(
                data={"status-code": 200, "time-weighted": seconds}, suceeded=True)
        except:
            response = Response(suceeded=False)
        return response
