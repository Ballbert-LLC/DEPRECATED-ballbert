import sys
import yaml
import socket
import json

from Hal import initialize_assistant
from Config import Config

assistant = initialize_assistant()

repos_path = "./Skills"
configuration = Config()


def handle_add(client, json_data):
    try:
        if (
            assistant.skill_manager.add_skill_from_url(assistant, json_data["url"])
            != False
        ):
            response = {"status_code": 200}
        else:
            response = {"status_code": 500}
    except Exception as e:
        print(e)
        response = {"status_code": 500}

    client.sendall(json.dumps(response).encode())


def handle_remove(client, json_data):
    try:
        assistant.skill_manager.remove_skill(json_data["skill_name"], assistant)
        response = {"status_code": 200}
    except Exception as e:
        response = {"status_code": 500, "error": str(e)}

    client.sendall(json.dumps(response).encode())


def handle_config(client, json_data):
    try:
        values = json_data["values"]

        for name, value in values.items():
            skill = name.split("-")[0]
            field = name.split("-")[1]

            settingsPath = os.path.join(repos_path, skill, "settings.yaml")
            if value == "True" or value == "true":
                value = True

            if socket.gethostname() == "YOUR_HOSTNAME":
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

    client.sendall(json.dumps(response).encode())


def handle_request(client):
    request_data = client.recv(4096).decode()
    json_data = json.loads(request_data)

    endpoint = json_data.get("endpoint")

    if endpoint == "/add_skill":
        handle_add(client, json_data)
    elif endpoint == "/remove_skill":
        handle_remove(client, json_data)
    elif endpoint == "/config":
        handle_config(client, json_data)
    else:
        response = {"status_code": 404}
        client.sendall(json.dumps(response).encode())

    client.close()


def run():
    print("bouta run")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))
    server.listen(5)

    while True:
        client, address = server.accept()
        handle_request(client)


if __name__ == "__main__":
    run()
