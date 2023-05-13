import os
import shutil
import uuid

import yaml
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, send
from git import Repo

from ..Hal import assistant

repos_path = "./Skills"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

locals_images = []


@app.route('/')
def index():
    return render_template('index.html', totalDevicesOnline=5)


@app.route('/skills', methods=["GET", "POST"])
def skills():
    print(locals_images)
    return render_template("skills.html", installedSkills=locals_images)


@app.route('/addons')
def addons():
    return render_template('index.html', totalDevicesOnline=5)


@app.route('/config')
def config():
    settings = assistant.skill_manager.get_settings_meta(
        assistant.installed_skills)
    return render_template('config.html', settings=settings)


@app.route('/settings')
def settings():
    return render_template('index.html', totalDevicesOnline=5)


@socketio.on('addSkill')
def handle_json(json):
    global locals_images
    # try:
    if assistant.add_skill_from_url(json["url"]) != False:
        send({"status_code": 200}, json=True)
    else:
        send({"status_code": 500}, json=True)

    locals_images = []
    prepare_files()
    # except:
    #     send({"status_code": 500}, json=True)


@socketio.on('rmSkill')
def handle_remove(json):
    try:
        global locals_images
        assistant.remove_skill(json["skill_name"])
        locals_images = []
        prepare_files()
        send({"status_code": 200}, json=True)
    except Exception as e:
        send({"status_code": 500, "error": e}, json=True)


@socketio.on('config')
def handle_remove(json):
    values = json["values"]
    for name, value in values.items():
        skill = name.split(".")[0]
        field = name.split(".")[1]

        settingsPath = os.path.join(repos_path, skill, "settings.yaml")
        if value == "True" or value == "true":
            value = True

        if os.path.exists(settingsPath):

            with open(settingsPath, 'r') as f:
                existing_yaml = yaml.safe_load(f)

            if not existing_yaml or isinstance(existing_yaml, str):
                existing_yaml = {}

            obj = {field: value}

            # Merge existing YAML with new data
            merged_yaml = {**existing_yaml, **obj}

            # Write merged YAML to output file
            with open(settingsPath, 'w') as f:
                yaml.dump(merged_yaml, f, default_flow_style=False)

        print(skill, field, value)
    print("-----------------")


def prepare_files():
    for item in assistant.installed_skills:
        result = item.copy()

        new_file_name = str(uuid.uuid4())
        shutil.copyfile(item["image"], os.path.join(
            "./Hal/Flask/Static/images", new_file_name))

        result["image"] = new_file_name
        locals_images.append(result)


def run():
    prepare_files()

    socketio.run(app, use_reloader=True,  extra_files=[
                 "A:\\hal\\Hal\\Flask\\templates\\index.html", "A:\\hal\\Hal\\Flask\\templates\\config.html"])
