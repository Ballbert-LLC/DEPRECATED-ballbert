import re
import sqlite3
import time
import uuid
from Config import Config
import os
import shutil
import speech_recognition as sr
from pvrecorder import PvRecorder
import speech_recognition as sr


def rmtree_hard(path, _prev=""):
    try:
        shutil.rmtree(path)
    except PermissionError as e:
        if e == _prev:
            return
        match = re.search(r"Access is denied: '(.*)'", str(e))
        if match:
            file_path = match.group(1)
            os.chmod(file_path, 0o777)

            # Delete the file
            os.remove(file_path)
            rmtree_hard(path, _prev=e)
        else:
            raise e


def setup():
    config = Config()

    os.remove("skills.db")

    if not os.path.exists("./temp"):
        os.makedirs("./temp")

    init_temp_path = os.path.join("./temp", str(uuid.uuid4()))
    shutil.copy2("./Skills/__init__.py", init_temp_path)

    for file in os.listdir("./Skills"):
        if os.path.isdir(os.path.join(os.path.abspath("./Skills"), file)):
            rmtree_hard(os.path.join(os.path.abspath("./Skills"), file))

    shutil.move(init_temp_path, "./Skills/__init__.py")

    con = sqlite3.connect("skills.db")

    cur = con.cursor()

    try:
        cur.execute(
            "CREATE TABLE actions(skill, action_uuid, action_id, action_name, action_paramiters)"
        )

        cur.execute("CREATE TABLE installedSkills(skill, version)")

        cur.execute("CREATE TABLE requirements(url, name, requiredBy)")
    except:
        print("already exists")

    con.commit()

    con.close()

    sr_mics = {}
    pv_mics = {}

    def sr_microphones():
        mic_list = sr.Microphone.list_microphone_names()
        for index, mic_name in enumerate(mic_list):
            if mic_name not in sr_mics:
                sr_mics[mic_name] = index

    # Call the function to list the microphones
    sr_microphones()

    def pv_microphones():
        audio_devices = PvRecorder.get_audio_devices()
        for index, device in enumerate(audio_devices):
            pv_mics[device] = index

    # Call the function to list the microphones
    pv_microphones()

    def get_common_values(dict1, dict2):
        common_values = []

        for value in dict1.keys():
            if value in dict2.keys():
                common_values.append(value)

        return common_values

    common = get_common_values(sr_mics, pv_mics)

    for index, item in enumerate(common):
        print(f"{index}: {item}")

    index = int(input("Which device do you want to pick (the number): "))

    device = common[index]

    pv_mic = pv_mics[device]
    sr_mic = sr_mics[device]

    config["PV_MIC"] = pv_mic
    config["SR_MIC"] = sr_mic
