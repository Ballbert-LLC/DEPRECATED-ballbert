from docstring_parser import parse


def parse_function_docstring(func):
    """
    Parses the docstring of a given function.

    :param func: The function whose docstring needs to be parsed.
    :type func: function
    :return: The parsed docstring.
    :rtype: Docstring
    """
    print(func.__doc__)
    docstring = parse(func.__doc__)
    return docstring


import random
import time
from math import sqrt

from Hal.Classes import Response
from Hal.Decorators import reg
from Hal.Skill import Skill

def add(self, a, b):
    """Calculate the distance between two points.

    Parameters
    ----------
    x : `float`
        X-axis coordinate.
    y : `float`
        Y-axis coordinate.
    x0 : `float`, optional
        X-axis coordinate for the second point (the origin,
        by default).

        Descriptions can have multiple paragraphs, and lists:

        - First list item.
        - Second list item.
    y0 : `float`, optional
        Y-axis coordinate for the second point (the origin,
        by default).
    **kwargs
        Additional keyword arguments passed to
        `calcExternalApi`.
    """
    a = int(a)
    b = int(b)
    return Response(suceeded=True, data=a+b)

# Call the parse_function_docstring function with the example_function
parsed_docstring = parse_function_docstring(add)

print(parsed_docstring.style)
print(parsed_docstring.params[1].is_optional)
