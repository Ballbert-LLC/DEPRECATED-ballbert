from docstring_parser import parse


def parse_function_docstring(func):
    """
    Parses the docstring of a given function.

    :param func: The function whose docstring needs to be parsed.
    :type func: function
    :return: The parsed docstring.
    :rtype: Docstring
    """
    docstring = parse(func.__doc__)
    return docstring


# Example function with a docstring
def example_function(name, priority, sender):
    """
    Short description

    Long description spanning multiple lines
    - First line
    - Second line
    - Third line

    :param str? name: description 1
    :param int priority: description 2
    :param str sender: description 3
    :raises ValueError: if name is invalid
    """
    pass


# Call the parse_function_docstring function with the example_function
parsed_docstring = parse_function_docstring(example_function)

# Access the parsed docstring information
print(parsed_docstring.short_description)
print(parsed_docstring.long_description)
print(parsed_docstring.params[0].is_optional)
print(parsed_docstring.raises)
