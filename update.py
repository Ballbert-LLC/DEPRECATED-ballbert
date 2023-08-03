import os
import sys
import shutil
from Config import Config

config = Config()

BACKUP_PATH = sys.argv[1]
NEW_VERSION = sys.argv[2]

paths = [
    ".env",
    "skills.db",
    "logs.txt",
    "creds.json",
]

dir_paths = [
    "Skills",
    "Flask/static/images",
]

for path in paths:
    source_path = os.path.join(BACKUP_PATH, path)
    destination_path = os.path.join("./", path)

    if os.path.exists(destination_path):
        os.remove(destination_path)

    if not os.path.exists(source_path):
        break

    shutil.copy(source_path, destination_path)

for path in dir_paths:
    source_path = os.path.join(BACKUP_PATH, path)
    destination_path = os.path.join("./", path)

    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)

    if not os.path.exists(source_path):
        break

    shutil.copytree(source_path, destination_path)

config["CURRENT_VERSION"] = NEW_VERSION
print("Done!")
