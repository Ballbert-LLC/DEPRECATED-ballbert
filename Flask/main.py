import os
import shutil
import uuid

import yaml
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, send
from git import Repo
from Hal import initialize_assistant
from Config import Config

assistant = initialize_assistant()

repos_path = "./Skills"
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
configuration = Config()
locals_images = []


@app.route("/add_skill", methods=["POST"])
def handle_add():
    global locals_images
    try:
        json_data = request.get_json()
        if (
            assistant.skill_manager.add_skill_from_url(assistant, json_data["url"])
            != False
        ):
            locals_images = []
            prepare_files()
            return jsonify({"status_code": 200})
        else:
            locals_images = []
            prepare_files()
            return jsonify({"status_code": 500})

    except Exception as e:
        print(e)
        return jsonify({"status_code": 500})


@app.route("/remove_skill", methods=["POST"])
def handle_remove():
    try:
        global locals_images
        json_data = request.get_json()
        assistant.skill_manager.remove_skill(json_data["skill_name"], assistant)
        locals_images = []
        prepare_files()
        return jsonify({"status_code": 200})
    except Exception as e:
        return jsonify({"status_code": 500, "error": str(e)})


@app.route("/config", methods=["POST"])
def handle_config():
    try:
        json_data = request.get_json()
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

        return jsonify({"status_code": 200})
    except Exception as e:
        return jsonify({"status_code": 500, "error": str(e)})


def prepare_files():
    print("assistant:", assistant.installed_skills)
    for key, item in assistant.installed_skills.items():
        result = item.copy()

        new_file_name = str(uuid.uuid4())
        shutil.copyfile(
            item["image"], os.path.join("./Flask/Static/images", new_file_name)
        )

        result["image"] = new_file_name
        locals_images.append(result)


def run():
    print("bouta run")

    prepare_files()

    # causes problems
    should_reload = False

    if configuration.debug_mode and should_reload:
        socketio.run(
            app,
            use_reloader=True,
            extra_files=[
                "A:\\hal\\Hal\\Flask\\templates\\index.html",
                "A:\\hal\\Hal\\Flask\\templates\\config.html",
            ],
        )
    else:
        socketio.run(app, host="0.0.0.0")
