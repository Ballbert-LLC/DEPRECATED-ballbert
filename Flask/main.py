import datetime
import json
import os
import shutil
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
from fastapi import status, HTTPException
from Hal.Classes import HalExeption
from OTAWifi import set_wifi_credentials


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
        assistant.skill_manager.add_skill_from_url(assistant, json_data["url"])
    except HalExeption as e:
        raise HTTPException(
            status_code=e.error_code,
            detail=e,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=e,
        )
    else:
        response = {"status_code": 200}
        return response


@router.post("/remove_skill")
def remove_skill(json_data: dict):
    try:
        from Hal import initialize_assistant

        assistant = initialize_assistant()
    except HalExeption as e:
        raise HTTPException(
            status_code=e.error_code,
            detail=e,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=e,
        )

    try:
        response = assistant.skill_manager.remove_skill(
            json_data["skill_name"], assistant
        )
    except HalExeption as e:
        raise HTTPException(
            status_code=e.error_code,
            detail=e,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=e,
        )
    else:
        return response


@router.post("/config")
def handle_config(json_data: dict):
    try:
        if "values" not in json_data:
            raise HTTPException(
                status_code=400,
                detail="values not in json data",
            )

        values = json_data["values"]

        for name, value in values.items():
            try:
                skill = name.split("-")[0]
                field = name.split("-")[1]
            except Exception as e:
                continue

            settingsPath = os.path.join(repos_path, skill, "settings.yaml")
            if not os.path.exists(settingsPath):
                continue

            if value == "True" or value == "true":
                value = True

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

    except Exception as e:
        raise HTTPException(
            status_code=500,
        )
    else:
        response = {"status_code": 200}
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    else:
        return response


@router.get("/get_config")
def get_config(skill_name):
    try:
        from Hal import initialize_assistant

        assistant = initialize_assistant()
        response = {"status_code": 200}
        response["config"] = assistant.skill_manager.get_config(skill_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    return response


@router.get("/get_settings_meta_for_skill")
def get_settings_meta_for_skill(skill_name):
    try:
        from Hal import initialize_assistant

        assistant = initialize_assistant()
        response = {"status_code": 200}
        response["settings"] = assistant.skill_manager.get_settings_meta_for_skill(
            skill_name, assistant
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.get("/get_microphones")
def get_microphones():
    sr_mics = {}
    pv_mics = {}
    try:

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
        response = {"status_code": 200, "microphones": common}
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.post("/test_openai_api_key")
def test_openai_api_key(api_key):
    try:
        openai.api_key = api_key
        openai.Model.list()
    except openai.error.AuthenticationError:
        return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    else:
        return True


@router.post("/test_huggingface_api_key")
def test_huggingface_api_key(api_key):
    try:
        import requests

        API_URL = "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions"
        headers = {"Authorization": f"Bearer {api_key}"}

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()

        output = query(
            {
                "inputs": "Hi",
            }
        )

        return "error" not in output
    except Exception as e:
        return False


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

    try:
        cached_chat_models = get_chat_model_from_cache()
    except Exception as e:
        print("error getting cached models", e)

    if cached_chat_models:
        chat_models = cached_chat_models
    else:
        print("retreiving chat models")
        try:
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)

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

    if not ("variables" in json_data and json_data.items()):
        raise HTTPException(status_code=500, detail="invalid json")

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
                shutil.copyfile(file_path, "./creds.json")
                config["GOOGLE_APPLICATION_CREDENTIALS"] = "./creds.json"

                return True
            else:
                os.remove(file_path)
                return False
    except Exception as e:
        os.remove(file_path)
        print(e)
        return False
    finally:
        try:
            os.remove(file_path)
        except Exception as e:
            print(e)


@router.route("/save_credentials", methods=["GET", "POST"])
def save_credentials(json: dict):
    if "ssid" in json and "wifi_key" in json:
        ssid = json["ssid"]
        wifi_key = json["wifi_key"]
    else:
        raise HTTPException(status_code=400, detail="invalid json")

    try:
        set_wifi_credentials(ssid, wifi_key)
        return {"status": "success", "status_code": 200}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.post("/validate_file")
async def validate_file(file: UploadFile = File(...)):
    try:
        file_path = f"./{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        is_valid = is_valid_tts_service_account(file_path)
        return {"is_valid": is_valid}
    except Exception as e:
        return {"is_valid": False}


@router.get("/get_enviroment_variable")
def get_enviroment_variable(key):
    config = Config()
    if key in config:
        return {"key": config[key]}
    else:
        return None


@router.get("/get_all_env_variables")
def get_all_env_variables():
    config = Config()
    return config.data
