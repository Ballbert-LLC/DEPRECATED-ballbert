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


def run_web():
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles

    app = FastAPI()

    # Mount the router from the api module
    from Flask.main import router

    app.include_router(router)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
    )


def run_assistant():
    from Hal import assistant, initialize_assistant

    assistant_instance = initialize_assistant()

    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    time.sleep(1)

    assistant_instance.skill_manager.add_skill_from_url(
        assistant_instance, "https://github.com/seesi8/Personality.git"
    )

    assistant_instance.voice_to_voice_chat()


def main():
    print(config)
    if config["SETUP_MODE"]:
        import setup

        try:
            setup.setup()
        except:
            pass

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
