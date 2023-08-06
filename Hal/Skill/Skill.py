import os

import yaml

from ..Logging import log_line

repos_path = f"{os.path.abspath(os.getcwd())}/Skills"


class Skill:
    def __init__(self) -> None:
        pass

    def handle_yaml_err(self):
        path = f"{repos_path}/{self.__class__.__name__}/settings.yaml"

        if not os.path.exists(path):
            return

        os.remove(path)

        open(path, "w")

    def get(self, setting):
        if not os.path.exists(f"{repos_path}/{self.__class__.__name__}/settings.yaml"):
            return None
        with open(
            f"{repos_path}/{self.__class__.__name__}/settings.yaml", "r"
        ) as stream:
            try:
                result = yaml.safe_load(stream)
                if isinstance(result, str):
                    return None
                return result.get(setting)
            except yaml.YAMLError as e:
                log_line("Err", e)
                self.handle_yaml_err()
                return None
            except Exception as e:
                log_line("Err", e)
                return None
