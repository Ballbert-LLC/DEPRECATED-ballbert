import asyncio
import json
import os
import platform
import threading

import websockets


def log_line(message, *args):
    try:
        if not os.path.exists("./logs.txt"):
            open("./logs.txt", "w")
        for arg in args:
            try:
                message += arg
            except Exception as e:
                pass
        with open("./logs.txt", "a", encoding="utf-8") as f1:
            f1.write(message + os.linesep)
    except Exception as e:
        pass


def display_error():
    async def send_color_to_ws():
        async with websockets.connect("ws://localhost:8765") as websocket:
            json_data = json.dumps({"type": "color", "color": "red"})

            await websocket.send(json_data)

    def send_color_factory():
        try:
            asyncio.run(send_color_to_ws())
        except Exception as e:
            log_line("Err", e)

    try:
        t = threading.Thread(target=send_color_factory, args=())
        t.start()
    except Exception as e:
        log_line("Err", e)


def handle_error():
    if platform.system() == "Linux":
        os.system("sudo reboot")
