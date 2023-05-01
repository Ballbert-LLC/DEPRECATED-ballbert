import threading

from Hal import assistant, run


def main():
    from Hal import Action, Instruction
    assistant.text_chat()


if __name__ == "__main__":
    t = threading.Thread(target=run)
    t.start()

    main()
