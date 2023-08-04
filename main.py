import asyncio
import platform
import threading
import os
import multiprocessing
import threading
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.background import BackgroundTask
from Config import Config

config = Config()

# VOICE | TEXT
MODE = "VOICE"


def run_web():
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles

    app = FastAPI()

    def start_web():
        try:
            # Mount the router from the api module
            from Flask.main import router

            app.include_router(router)
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=5000,
            )
        except Exception as e:
            print("shut down")
            print("___________________________________")

    # Start the web server
    t = threading.Thread(target=start_web)
    t.daemon = True
    t.start()
    return t


def run_assistant():
    if os.path.exists("./UPDATE"):
        return
    time.sleep(1)

    from Hal import assistant, initialize_assistant

    assistant_instance = initialize_assistant()

    try:
        assistant_instance.skill_manager.add_skill_from_url(
            assistant_instance, "https://github.com/seesi8/Personality.git"
        )
    except Exception as e:
        print("e", e)
    try:
        if MODE == "VOICE":
            asyncio.run(assistant_instance.voice_to_voice_chat())
        else:
            asyncio.run(assistant_instance.text_chat())
    except Exception as e:
        print(e)


def run_gui():
    # Start the gui
    import GUI

    GUI.run_main()


def start_setup():
    import setup

    try:
        setup.setup()
    except Exception as e:
        print(e)


def ready_stage():
    if not config["CURRENT_STAGE"]:
        config["CURRENT_STAGE"] = 0


def run_update_manager():
    from Version_Manager import start_version_manager

    t = multiprocessing.Process(target=start_version_manager)

    t.start()
    return t


def main():
    should_run_gui = True

    try:
        ready_stage()

        while config["CURRENT_STAGE"] == 0:
            from OTAWifi import run_api

            run_gui()

            run_api()

        while config["CURRENT_STAGE"] == 1:
            web_thread = run_web()

            run_gui()
            start_setup()
            should_run_gui = False

        while config["CURRENT_STAGE"] == 2:
            web_thread = run_web()
            if should_run_gui:
                run_gui()
            if platform.system() == "Linux" and False:
                update_thread = run_update_manager()
            run_assistant()
    except Exception as e:
        print(e)
        update_thread.kill()


def setup_and_teardown():
    import sys

    if platform.system() == "Linux":
        sys.stdout = open("/etc/ballbert/logs.txt", "w")
    main()
    sys.stdout.close()


if __name__ == "__main__":
    setup_and_teardown()
