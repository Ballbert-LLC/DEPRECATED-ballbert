import asyncio
import functools
import json
import multiprocessing
import time
import websockets
from ..Sentament import sentament


def handle_messages(messages, queue: multiprocessing.Queue):
    while not queue.empty():
        queue.get()
    queue.put("E" + sentament.get_sentament(" ".join(messages)))


class Client:
    def __init__(self) -> None:
        self.messages = []
        self.user_message = None

    def clear_messages(self):
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

    def get_messages(self):
        return self.messages

    def set_user_message(self, message):
        self.user_message = message


async def handle_request(
    websocket, message, client: Client, queue: multiprocessing.Queue
):
    # Decode the message
    message = json.loads(message)

    print(message)
    # Get the message type
    message_type = message["type"]

    # Handle the message based on its type
    if message_type == "user" and "message" in message:
        client.set_user_message(message["message"])
    elif message_type == "assistant" and "message" in message and "is_final" in message:
        if not message["is_final"]:
            client.add_message(message["message"])
            handle_messages(client.messages, queue)
        else:
            client.add_message(message["message"])
            handle_messages(client.messages, queue)
            client.clear_messages()

            time.sleep(5)
            while not queue.empty():
                queue.get()
            queue.put("neutral")
    elif message_type == "color":
        queue.put("C" + message["color"])
    else:
        print(f"Unknown message type '{message_type}'.")


async def handle_client(websocket, path, queue: multiprocessing.Queue):
    try:
        client = Client()
        async for message in websocket:
            await handle_request(websocket, message, client, queue)  # Use "await" here

    except websockets.exceptions.ConnectionClosedOK:
        print("Client disconnected.")
    except Exception as e:
        print(f"Error: {e}")


async def main(queue=multiprocessing.Queue()):
    # Set the host and port for the WebSocket server
    host = "localhost"
    port = 8765

    # Create the WebSocket server
    server = await websockets.serve(
        functools.partial(handle_client, queue=queue), host, port
    )

    print(f"WebSocket server started at ws://{host}:{port}")

    # Keep the server running until terminated
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        print("WebSocket server stopped.")
