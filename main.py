import multiprocessing
import sys
import threading
import time


from Config import Config

config = Config()


def run_assistant():
    from Hal import assistant
    assistant.add_skill_from_url(
        "https://github.com/seesi8/HalAdvancedMath.git")

    time.sleep(5)
    assistant.remove_skill("SimpleMath")
    print(assistant.installed_skills)
    # assistant.text_chat()


def main():
    if "-setup" in sys.argv:
        import setup

    if config.ws:
        from Hal import run

        t = multiprocessing.Process(target=run)
        t.start()

    try:
        run_assistant()
    except:
        t.kill()
        print("Stoping")


if __name__ == "__main__":
    main()
