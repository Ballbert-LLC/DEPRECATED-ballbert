from Hal import assistant
import threading


def main():
    assistant.add_skill_from_url("https://github.com/seesi8/HalSimpleMath.git")


if __name__ == "__main__":
    main()
