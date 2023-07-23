import datetime
import json
import os
from fastapi import APIRouter, File, UploadFile
import openai
import tqdm
import yaml
from Config import Config
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import speech_recognition as sr
from pvrecorder import PvRecorder
import pvporcupine


router = APIRouter()


repos_path = "./Skills"


@router.get("/")
def root():
    return {"message": "Welcome to the API!"}


@router.post("/add_skill")
def add_skill(json_data: dict):
    from Hal import initialize_assistant

    assistant = initialize_assistant()
    try:
        if (
            assistant.skill_manager.add_skill_from_url(assistant, json_data["url"])
            is not False
        ):
            response = {"status_code": 200}
        else:
            response = {"status_code": 500}
    except Exception as e:
        print(e)
        response = {"status_code": 500}

    return response


@router.post("/remove_skill")
def remove_skill(json_data: dict):
    from Hal import initialize_assistant

    assistant = initialize_assistant()
    try:
        response = assistant.skill_manager.remove_skill(
            json_data["skill_name"], assistant
        )
    except Exception as e:
        response = {"status_code": 500, "error": str(e)}

    return response


@router.post("/config")
def handle_config(json_data: dict):
    try:
        values = json_data["values"]

        for name, value in values.items():
            skill = name.split("-")[0]
            field = name.split("-")[1]

            settingsPath = os.path.join(repos_path, skill, "settings.yaml")
            if value == "True" or value == "true":
                value = True

            if os.path.exists(settingsPath):
                with open(settingsPath, "r") as f:
                    existing_yaml = yaml.safe_load(f)

                if not existing_yaml or isinstance(existing_yaml, str):
                    existing_yaml = {}

                obj = {field: value}

                # Merge existing YAML with new data
                merged_yaml = {**existing_yaml, **obj}

                # Write merged YAML to output file
                with open(settingsPath, "w") as f:
                    yaml.dump(merged_yaml, f, default_flow_style=False)

        response = {"status_code": 200}
    except Exception as e:
        response = {"status_code": 500, "error": str(e)}

    return response


@router.get("/images/{image_path}")
async def get_image(image_path: str):
    # Assuming the images are stored in a directory named 'images'
    image_location = f"./Flask/static/images"
    image_path = os.path.join(image_location, image_path)
    if os.path.exists(image_path):
        # Return the image file as a response
        return FileResponse(image_path)
    else:
        return {"status_code": 500}


@router.get("/connected")
def connected():
    response = {"status_code": 200}
    return response


@router.get("/get_installed_skills")
def get_installed_skills():
    response = {"status_code": 200}

    try:
        from Hal import initialize_assistant

        assistant = initialize_assistant()
        response["skills"] = assistant.skill_manager.get_installed_skills(assistant)
        return response
    except:
        response = {"status_code": 500}
        return response


@router.get("/get_config")
def get_config(skill_name):
    from Hal import initialize_assistant

    assistant = initialize_assistant()
    response = {"status_code": 200}
    response["config"] = assistant.skill_manager.get_config(skill_name)
    return response


@router.get("/get_settings_meta_for_skill")
def get_settings_meta_for_skill(skill_name):
    from Hal import initialize_assistant

    assistant = initialize_assistant()
    response = {"status_code": 200}
    response["settings"] = assistant.skill_manager.get_settings_meta_for_skill(
        skill_name, assistant
    )
    return response


@router.get("/get_microphones")
def get_microphones():
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
    response = {"status_code": 200}
    response["microphones"] = common
    return response


@router.post("/test_openai_api_key")
def test_openai_api_key(api_key):
    openai.api_key = api_key

    try:
        openai.Model.list()
    except openai.error.AuthenticationError:
        return False
    else:
        return True


@router.get("/get_llms")
def get_llms(api_key):
    openai.api_key = api_key

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

    return chat_models


@router.post("/test_porcupine_api_key")
def test_porqupine_api_key(api_key):
    try:
        pvporcupine.create(
            access_key=api_key,
            keywords=["porcupine"],
        )
    except Exception as e:
        return False
    else:
        return True


@router.post("/set_enviroment_variables")
def set_enviroment_variables(json_data: dict):
    config = Config()

    for key, value in json_data["variables"].items():
        config[key] = value

    return {"status_code": 200}


def is_valid_tts_service_account(file_path):
    config = Config()
    try:
        with open(file_path) as file:
            service_account_data = json.load(file)
            # Check if the file contains the required keys
            if (
                "type" in service_account_data
                and "project_id" in service_account_data
                and "private_key_id" in service_account_data
                and "private_key" in service_account_data
                and "client_email" in service_account_data
                and "client_id" in service_account_data
                and "auth_uri" in service_account_data
                and "token_uri" in service_account_data
                and "auth_provider_x509_cert_url" in service_account_data
                and "client_x509_cert_url" in service_account_data
            ):
                config["GOOGLE_APPLICATION_CREDENTIALS"] = file_path
                return True
            else:
                os.remove(file_path)
                return False
    except:
        os.remove(file_path)
        return False


@router.post("/validate_file")
async def validate_file(file: UploadFile = File(...)):
    file_path = f"./{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    is_valid = is_valid_tts_service_account(file_path)
    return {"is_valid": is_valid}


@router.get("/get_enviroment_variable")
def get_enviroment_variable(key):
    config = Config()
    if key in config:
        return {"key": config[key]}
    else:
        return None
