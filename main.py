from Hal import assistant
import threading


def main():
    from Hal import Action, Instruction
    assistant.add_skill("SimpleMath")
    assistant.text_chat()


if __name__ == "__main__":

    main()
