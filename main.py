from Hal import assistant
import threading


def main():
    from Classes import Action, Instruction
    assistant.add_skill("Demo_Skills")
    assistant.text_chat()


if __name__ == "__main__":

    main()
