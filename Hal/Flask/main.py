import os
import uuid

import yaml
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, send
from git import Repo

repos_path = "./repos"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html', totalDevicesOnline=5)


ButtonPressed = 0


@app.route('/skills', methods=["GET", "POST"])
def skills():
    global ButtonPressed
    if request.method == "POST":
        ButtonPressed += 1
        return render_template("skills.html", ButtonPressed=ButtonPressed)
        # I think you want to increment, that case ButtonPressed will be plus 1.
    return render_template("skills.html", ButtonPressed=ButtonPressed)


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
    try:
        add_skill_to_path(json["url"])
        send({"status_code": 200}, json=True)

    except:
        send({"status_code": 500}, json=True)


def add_skill_to_path(url):
    Repo.clone_from(url, f"{repos_path}/temp")
    name = ""
    requirements = []
    with open(f"{repos_path}/temp/config.yaml", 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        name = data_loaded["name"] if data_loaded["name"] else uuid.uuid4()
        print(data_loaded)
        requirements = data_loaded["requirements"] if "requirements" in data_loaded else [
        ]

    open(f"{repos_path}/temp/settings.yaml", 'w').close()

    os.rename(f"{repos_path}/temp", f"{repos_path}/{name}")

    for requirement in requirements:
        add_skill_to_path(requirement)


def run():
    socketio.run(app)
