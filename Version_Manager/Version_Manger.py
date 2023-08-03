import os
import shutil
import time

import requests
from Config import Config

config = Config()
API_KEY = config["GITHUB"]


def sleep_for_time():
    if not API_KEY:
        time.sleep(100)
    else:
        time.sleep(1)


def get_latest_release(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
    if API_KEY:
        headers = {"Authorization": f"token {API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        releases = response.json()
        # Sort releases based on the published date, with the latest first
        releases.sort(key=lambda r: r["published_at"], reverse=True)
        for release in releases:
            if not release["prerelease"]:
                return release["tag_name"]
    return None


def make_backup(current_release):
    backup_dir = os.path.abspath(
        os.path.join("../", "ballbert_backups", current_release)
    )
    if os.path.exists(backup_dir):
        os.system(f"rd /s /q {backup_dir} ")

    shutil.copytree("./", backup_dir)


def alert_for_update():
    open("./UPDATE", "w").close()
    time.sleep(10)
    if os.path.exists("./UPDATE") and not os.path.exists("./NOUPDATE"):
        os.remove("./UPDATE")
        return True
    else:
        os.remove("./UPDATE")
        if os.path.exists("./NOUPDATE"):
            os.remove("./NOUPDATE")
        return False


def update_version(current_release, latest_release):
    make_backup(current_release)
    if not alert_for_update():
        raise (Exception("Update Refused By Another Process"))
    return latest_release


def start_version_manager():
    while True:
        sleep_for_time()
        latest_release = get_latest_release("Ballbert-LLC", "ballbert")
        current_release = config["CURRENT_VERSION"] or "0"
        print(current_release, latest_release)
        if not latest_release:
            print("Unable to retrieve the latest release.")
            continue

        if latest_release == current_release:
            continue

        try:
            new_version = update_version(current_release, latest_release)
        except Exception as e:
            print(e)
        else:
            config["CURRENT_VERSION"] = new_version
