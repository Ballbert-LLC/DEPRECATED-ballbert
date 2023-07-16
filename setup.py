import datetime
import json
import re
import sqlite3
import time
import uuid
import pvporcupine
import openai
import tqdm
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

    open("skills.db", "w").close()

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

    config["TEMPATURE"] = 0.5

    # Microphone

    # sr_mics = {}
    # pv_mics = {}

    # def sr_microphones():
    #     mic_list = sr.Microphone.list_microphone_names()
    #     for index, mic_name in enumerate(mic_list):
    #         if mic_name not in sr_mics:
    #             sr_mics[mic_name] = index

    # # Call the function to list the microphones
    # sr_microphones()

    # def pv_microphones():
    #     audio_devices = PvRecorder.get_audio_devices()
    #     for index, device in enumerate(audio_devices):
    #         pv_mics[device] = index

    # # Call the function to list the microphones
    # pv_microphones()

    # def get_common_values(dict1, dict2):
    #     common_values = []

    #     for value in dict1.keys():
    #         if value in dict2.keys():
    #             common_values.append(value)

    #     return common_values

    # common = get_common_values(sr_mics, pv_mics)

    # for index, item in enumerate(common):
    #     print(f"{index}: {item}")

    # index = int(input("Which device do you want to pick (0): ") or "0")
    # index = 0

    # device = common[index]

    # pv_mic = pv_mics[device]
    # sr_mic = sr_mics[device]

    config["PV_MIC"] = 1
    config["SR_MIC"] = 1

    while True:
        if config.isReady():
            break

    config["SETUP_MODE"] = False


def terminal_setup():
    config = Config()

    # Openai api key

    while True:
        api_key = input("What is your openai api key? ")

        openai.api_key = api_key

        try:
            openai.Model.list()
        except openai.error.AuthenticationError:
            print("Invalid API key Try agian")
        else:
            break

    config["OPENAI_API_KEY"] = api_key

    # LLM
    chat_models = []

    def get_chat_model_from_cache():
        if os.path.exists("chatModels.cache.json"):
            with open("chatModels.cache.json", "r") as file:
                cache = file.read()
                cache = json.loads(cache)

                now = datetime.datetime.now()
                then = datetime.datetime.fromisoformat(cache["dateTime"])
                diff = now - then
                diff = diff.days

                if diff <= 7:
                    chat_models = cache["models"]
                    return chat_models
                else:
                    return []
        else:
            return []

    cached_chat_models = get_chat_model_from_cache()

    if cached_chat_models:
        chat_models = cached_chat_models
    else:
        print("retreiving chat models")

        models = openai.Model.list()["data"]

        length = len(models)

        pbar = tqdm(total=length)  # Init pbar

        for item in models:
            model = item["id"]
            try:
                openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": "Say only the leter L"}],
                    functions=[
                        {
                            "name": "example",
                            "parameters": {"type": "object", "properties": {}},
                        }
                    ],
                )
            except Exception as e:
                pass
            else:
                chat_models.append(model)
            finally:
                pbar.update(n=1)
        pbar.close()

        file = open("chatModels.cache.json", "w")
        file.writelines(
            json.dumps(
                {
                    "dateTime": str(datetime.datetime.now()),
                    "models": chat_models,
                }
            )
        )
        file.close()

    for i, model in enumerate(chat_models):
        print(f"{i}: {model}")

    llm = chat_models[int(input("Which model do you want to pick (0): ") or "0")]

    config["LLM"] = llm

    # Tempature

    def clamp(n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n

    print(
        "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic."
    )

    temp = clamp(
        float(
            input("What tempature do you want 0-2. If unsure use default. (0.5): ")
            or "0.5"
        ),
        0,
        2,
    )

    config["TEMPATURE"] = temp

    # Porqupine

    while True:
        try:
            porqupine_api_key = input("What is your porqupine api key? ")
            pvporcupine.create(
                access_key=porqupine_api_key,
                keywords=["porcupine"],
            )
        except Exception as e:
            print("Invalid API key Try agian")
        else:
            break

    config["PORQUPINE_API_KEY"] = porqupine_api_key
