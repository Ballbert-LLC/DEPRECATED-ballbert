import asyncio
import multiprocessing
import time


def run_app(queue: multiprocessing.Queue):
    from .KivyApp import App

    application = App()

    application.run(queue)


def run_ws(queue: multiprocessing.Queue):
    from .WS import main

    asyncio.run(main(queue))


def run_main():
    q = multiprocessing.Queue()

    app = multiprocessing.Process(target=run_app, args=(q,))
    app.start()

    ws = multiprocessing.Process(target=run_ws, args=(q,))
    ws.start()
