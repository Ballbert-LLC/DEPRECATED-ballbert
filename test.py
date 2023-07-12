import datetime
import json
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
import openai
from tqdm import tqdm
import pvporcupine

config = Config()


def setup():
    # Microphone

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

    index = int(input("Which device do you want to pick (0): ") or "0")

    device = common[index]

    pv_mic = pv_mics[device]
    sr_mic = sr_mics[device]

    config["PV_MIC"] = pv_mic
    config["SR_MIC"] = sr_mic

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

    temp = float(
        input("What tempature do you want 0-2. If unsure use default. (0.5): ") or "0.5"
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

    config["SETUP_MODE"] = False


setup()
