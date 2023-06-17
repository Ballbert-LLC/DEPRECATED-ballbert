import ast
import json
import threading
import os
import re
import shutil
import sys
import threading
import time
import types


from Config import Config

config = Config()


def rmtree_hard(path, _prev=""):
    try:
        shutil.rmtree(path)
    except PermissionError as e:
        if e == _prev:
            return
        match = re.search(r"Access is denied: '(.*)'", str(e))
        if match:
            file_path = match.group(1)
            os.chmod(file_path, 0o777)

            # Delete the file
            os.remove(file_path)
            rmtree_hard(path, _prev=e)
        else:
            raise e


def convert_dict_to_json_serializable(input_dict):
    # Convert non-serializable types to serializable equivalents
    serializable_dict = {}
    if isinstance(input_dict, dict):
        for key, value in input_dict.items():
            if isinstance(value, dict):
                value = convert_dict_to_json_serializable(value)
            elif isinstance(value, (list, tuple)):
                value = [convert_dict_to_json_serializable(v) for v in value]
            elif isinstance(value, set):
                value = [convert_dict_to_json_serializable(v) for v in value]
            elif isinstance(value, bytes):
                value = value.decode("utf-8")
            elif isinstance(value, types.FunctionType):
                value = value.__name__  # Replace function with its name
            elif isinstance(value, type):
                value = value.__name__  # Replace class with its name
            elif isinstance(value, types.FunctionType):
                value = value.__name__  # Replace function with its name
            serializable_dict[key] = value
    else:
        value = input_dict
        if isinstance(value, dict):
            value = convert_dict_to_json_serializable(value)
        elif isinstance(value, (list, tuple)):
            value = [convert_dict_to_json_serializable(v) for v in value]
        elif isinstance(value, set):
            value = [convert_dict_to_json_serializable(v) for v in value]
        elif isinstance(value, bytes):
            value = value.decode("utf-8")
        elif isinstance(value, types.FunctionType):
            value = value.__name__  # Replace function with its name
        elif isinstance(value, type):
            value = value.__name__  # Replace class with its name
        elif isinstance(value, types.FunctionType):
            value = value.__name__  # Replace function with its name

    return serializable_dict


def run_assistant():
    from Hal import assistant, initialize_assistant
    from Flask import run

    assistant_instance = initialize_assistant()

    # assistant_instance.add_skill_from_url(
    #     "https://github.com/seesi8/HalAdvancedMath.git")

    # print(assistant_instance.call_function(
    #     "advancedmath.get_num", (10,)).data)

    if config.ws:
        t = threading.Thread(target=run)
        t.daemon = True
        t.start()
    print(assistant_instance.action_dict)

    assistant_instance.text_chat()


def main():
    if "-setup" in sys.argv:
        import setup

        print("seting up")
        try:
            setup.setup()
        except:
            pass

    print("done with setup")
    try:
        run_assistant()
    except Exception as e:
        print(e)
        raise e


def setup_and_teardown():
    main()

    # if config.debug_mode:
    #     main()
    # else:
    #     rmtree_hard("./Flask/Static/images")
    #     os.mkdir("./Flask/Static/images")
    #     try:
    #         main()
    #     except Exception as e:
    #         rmtree_hard("./Flask/Static/images")
    #         os.mkdir("./Flask/Static/images")
    #         print(e)


if __name__ == "__main__":
    setup_and_teardown()
