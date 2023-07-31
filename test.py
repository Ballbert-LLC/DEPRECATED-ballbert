import asyncio
import json
import threading
import time

import websockets
from GUI import run_main


async def send_color_to_ws(color):
    async with websockets.connect("ws://localhost:8765") as websocket:
        json_data = json.dumps({"type": "color", "color": color})

        await websocket.send(json_data)


def send_color_factory(color):
    try:
        asyncio.run(send_color_to_ws(color))
    except Exception as e:
        print(e)


def send_color():
    t = threading.Thread(target=send_color_factory)
    t.start()
    return t


if __name__ == "__main__":
    colors = ["blue", "yellow", "red", "green", "grey"]
    run_main()
    index = 0
    while True:
        index += 1

        time.sleep(1)
        send_color_factory(colors[index])
        if index == len(colors) - 1:
            index = 0
