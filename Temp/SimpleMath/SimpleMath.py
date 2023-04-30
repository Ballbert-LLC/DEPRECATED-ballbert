import random
import time

from Hal.Classes import Response
from Hal.Decorators import reg


class SimpleMath:
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
