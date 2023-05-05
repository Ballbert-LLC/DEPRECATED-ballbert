import os
import shutil
import uuid

import yaml
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, send
from git import Repo
from ..Hal import assistant

repos_path = "./repos"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

locals_images = []


@app.route('/')
def index():
    return render_template('index.html', totalDevicesOnline=5)


@app.route('/skills', methods=["GET", "POST"])
def skills():
    return render_template("skills.html", installedSkills=locals_images)


@app.route('/addons')
def addons():
    return render_template('index.html', totalDevicesOnline=5)


@app.route('/config')
def config():
    return render_template('index.html', totalDevicesOnline=5)


@app.route('/settings')
def settings():
    return render_template('index.html', totalDevicesOnline=5)


@socketio.on('addSkill')
def handle_json(json):
    # try:
    if assistant.add_skill_from_url(json["url"]) != False:
        send({"status_code": 200}, json=True)
    else:
        send({"status_code": 500}, json=True)

    # except:
    #     send({"status_code": 500}, json=True)


def prepare_files():
    for item in assistant.installed_skills:
        result = item.copy()

        new_file_name = str(uuid.uuid4())
        shutil.copyfile(item["image"], os.path.join(
            "./Hal/Flask/Static", new_file_name))

        result["image"] = new_file_name
        locals_images.append(result)


def run():
    prepare_files()

    socketio.run(app)
