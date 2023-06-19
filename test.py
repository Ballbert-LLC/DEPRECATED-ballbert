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
    Calculate the total price based on the unit price and quantity.

    Args:
        unit_price (float): The price per unit of the item.
        quantity (int, optional): The number of items. Defaults to 1.

    Returns:
        float: The total price of the items.

    Raises:
        ValueError: If the unit price or quantity is negative.

    Examples:
        >>> calculate_total_price(10.5, 3)
        31.5
        >>> calculate_total_price(5.25)
        5.25
    """
    pass


# Call the parse_function_docstring function with the example_function
parsed_docstring = parse_function_docstring(example_function)

# Access the parsed docstring information
print(parsed_docstring.short_description)
print(parsed_docstring.examples[0].description)
print(parsed_docstring.params[1].is_optional)
print(parsed_docstring.raises)
