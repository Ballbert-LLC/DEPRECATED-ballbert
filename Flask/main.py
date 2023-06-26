import os
from fastapi import APIRouter
import yaml
from Hal import initialize_assistant
from Config import Config

router = APIRouter()
assistant = initialize_assistant()

repos_path = "./Skills"
configuration = Config()


@router.get("/")
def root():
    return {"message": "Welcome to the API!"}


@router.post("/add_skill")
def add_skill(json_data: dict):
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
    try:
        assistant.skill_manager.remove_skill(json_data["skill_name"], assistant)
        response = {"status_code": 200}
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
