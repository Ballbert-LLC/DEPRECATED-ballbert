from ..Classes import Response


def responses_to_string(actions: list[Response]) -> str:
    data = ""

    for action in actions:
        action_data = str(action.data)
        action_data.replace(" ", "")
        action_data.replace("'", "")
        action_data.replace('"', "")
        data += action_data

    return data
