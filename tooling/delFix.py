import os

files = []

for item in os.walk(os.path.abspath("./")):
    if not ".git" in item[0]:
        for file in item[2]:
            files.append(f"{item[0]}\\{file}".replace("\\", "\\\\"))
            print(f"{item[0]}\\{file}".replace("\\", "\\\\"))

print(" ".join(files))
