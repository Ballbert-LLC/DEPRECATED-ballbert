import os
import sys
import shutil

BACKUP_PATH = sys.argv[1]

paths = [
    ".env",
    "skills.db",
    "logs.txt",
    "creds.json",
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

print("Done!")
