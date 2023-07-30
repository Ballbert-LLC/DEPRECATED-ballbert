import asyncio
import threading
import os
import re
import shutil
import threading
import time
import types


from Config import Config

config = Config()


def run_web():
    def start_web():
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

    # Start the web server
    t = threading.Thread(target=start_web)
    t.daemon = True
    t.start()
    return t


def run_assistant():
    from Hal import assistant, initialize_assistant

    assistant_instance = initialize_assistant()

    assistant_instance.skill_manager.add_skill_from_url(
        assistant_instance, "https://github.com/seesi8/Personality.git"
    )

    asyncio.run(assistant_instance.voice_to_voice_chat())


def run_gui():
    # Start the gui
    import GUI

    GUI.run_main()


def start_setup():
    while config["CURRENT_STAGE"] == 1:
        import setup

        try:
            setup.setup()
        except Exception as e:
            print(e)


def main():
    run_gui()

    if not "CURRENT_STAGE" in config:
        config["CURRENT_STAGE"] = 0

    try:
        config["CURRENT_STAGE"]
    except:
        config["CURRENT_STAGE"] = 0

    while config["CURRENT_STAGE"] == 0:
        from OTAWifi import run_api

        run_api()

    web_thread = run_web()

    time.sleep(1)
    start_setup()

    try:
        run_assistant()
        pass
    except Exception as e:
        print(e)
        raise e


def setup_and_teardown():
    try:
        main()
    except Exception as e:
        print(e)
        main()


if __name__ == "__main__":
    setup_and_teardown()
