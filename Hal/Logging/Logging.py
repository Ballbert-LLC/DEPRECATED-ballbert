import os


def log_line(message):
    with open('./logs.txt', 'a', encoding="utf-8") as f1:
        f1.write(message + os.linesep)
