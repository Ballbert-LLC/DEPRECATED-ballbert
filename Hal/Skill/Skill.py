import os

import yaml
repos_path = f"{os.path.abspath(os.getcwd())}/Skills"


class Skill:
    def __init__(self) -> None:
        pass

    def get(self, setting):
        with open(f"{repos_path}/{self.__class__.__name__}/settings.yaml", "r") as stream:
            try:
                result = yaml.safe_load(stream)
                return result[setting]
            except yaml.YAMLError as exc:
                print(exc)
