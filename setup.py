import re
import sqlite3
import uuid
from Config import Config
import os
import shutil


def rmtree_hard(path, _prev=""):
    try:
        shutil.rmtree(path)
    except PermissionError as e:
        if e == _prev:
            return
        match = re.search(r"Access is denied: '(.*)'", str(e))
        if match:
            file_path = match.group(1)
            os.chmod(
                file_path, 0o777)

            # Delete the file
            os.remove(
                file_path)
            rmtree_hard(path, _prev=e)
        else:
            raise e


config = Config()


print(config.debug_mode)

if config.debug_mode:
    os.remove("skills.db")
    open("skills.db", "w").close()

    if not os.path.exists("./temp"):
        os.makedirs("./temp")

    init_temp_path = os.path.join("./temp", str(uuid.uuid4()))
    shutil.copy2("./Skills/__init__.py", init_temp_path)

    for file in os.listdir(".\\Skills"):
        if os.path.isdir(os.path.join(os.path.abspath(".\\Skills"), file)):
            rmtree_hard(os.path.join(os.path.abspath(".\\Skills"), file))

    shutil.move(init_temp_path, "./Skills/__init__.py")


con = sqlite3.connect("skills.db")

cur = con.cursor()

try:
    print("Creating")
    cur.execute(
        "CREATE TABLE actions(skill, action_uuid, action_id, action_name, action_paramiters)")

    cur.execute("CREATE TABLE installedSkills(skill, version)")

    cur.execute("CREATE TABLE requirements(required, requiredBy)")
except:
    print("already exists")
