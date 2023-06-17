import ast
from types import NoneType
import openai
import inspect
import shutil
import sqlite3
import uuid

import yaml
from git import Repo
import importlib

from . import Assistant
from ..Decorators import paramRegistrar, reg

import os
from Config import Config
from ..Utils import rmtree_hard

config = Config()

repos_path = f"{os.path.abspath(os.getcwd())}/Skills"


class SkillMangager:
    def __init__(self) -> None:
        pass

    def add_skill(self, assistant, skill, should_replace=True):
        con = sqlite3.connect("skills.db")

        cur = con.cursor()

        prev_action_dict = assistant.action_dict.copy()

        module = importlib.import_module(f"Skills.{skill}")

        desired_class = getattr(module, skill)

        new_action_dict: dict = {}
        print(skill)
        print(f"REG:// {reg.all}")
        # Adds into attributes
        action_dict: dict = reg.all

        for skill_id, item in action_dict.items():
            _parameters = tuple(inspect.signature(item["function"]).parameters.items())

            if skill_id not in prev_action_dict:
                new_action_dict[skill_id] = item
                new_action_dict[skill_id]["parameters"] = {}

            action_dict[skill_id]["parameters"] = (
                action_dict[skill_id]["parameters"]
                if "parameters" in action_dict[skill_id]
                else {}
            )

            for argument in _parameters:
                _name = argument[0]
                _type = (
                    f"<{argument[1].annotation}>"
                    if type(argument[1].annotation) is str
                    else f"<{argument[0]}>"
                )
                if skill_id not in prev_action_dict:
                    new_action_dict[skill_id]["parameters"][_name] = _type
                action_dict[skill_id]["parameters"][_name] = _type

        # Adds into attributes

        con.commit()

        image = self.get_image_url(skill=skill)

        class_instance = desired_class()

        functions_with_reg_decorator = dict()

        for name, value in inspect.getmembers(class_instance):
            if inspect.ismethod(value) and hasattr(value, "__func__"):
                if name in [
                    value["func_name_in_class"] for key, value in reg.all.items()
                ]:
                    functions_with_reg_decorator[name] = value.__func__

        for func_name, func in functions_with_reg_decorator.items():
            for action_name, values in action_dict.items():
                if func_name == values["func_name_in_class"]:

                    def wrapper_func_factory(func):
                        def wrapper_func(*args, **kwargs):
                            signature = inspect.signature(func)
                            if len(signature.parameters) > 0:
                                return func(class_instance, *args, **kwargs)
                            else:
                                return func(*args, **kwargs)

                        return wrapper_func

                    values["function"] = wrapper_func_factory(func)
                    values["class_instance"] = class_instance
                    action_dict[action_name] = values

        assistant.installed_skills[skill] = {
            "image": image,
            "name": skill,
            "version": 0.0,
            "actions": functions_with_reg_decorator,
            "class": class_instance,
        }

        assistant.action_dict = action_dict

    def get_image_url(self, skill):
        if os.path.exists(os.path.join(repos_path, skill, "icon.png")):
            image = os.path.join(repos_path, skill, "icon.png")
        else:
            res = ""

            description = res or None

            with open(f"{repos_path}/{skill}/config.yaml", "r") as stream:
                data_loaded = yaml.safe_load(stream)
                name = data_loaded["name"]
                description = (
                    data_loaded["description"]
                    if "description" in data_loaded
                    else "No description provided"
                )

            # Open a connection to the database file
            conn = sqlite3.connect("skills.db")

            # Create a cursor object to execute SQL commands
            cursor = conn.cursor()

            # Execute a SELECT query on the actions table
            cursor.execute("SELECT * FROM actions WHERE skill = ?", (name,))

            # Fetch all the rows returned by the query
            actions_data = cursor.fetchall()

            # Close the cursor and the database connection
            cursor.close()
            conn.close()

            des = ""
            for row in actions_data:
                des += f"      Name: {row[3]}, Paramiters: {row[4]}\n"

            result = f"""

                Name of skill:
                    {name}

                Description of skill:
                    {description}

                Actions:
            {des}

            """

            prompt = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a prompt generator for an image generator that. Your prompts are made to be an turn into an icon for a skill addon with the details in the paramiters the user provides. Constraints: Speak in language that an image generator could understand.",
                    },
                    {"role": "user", "content": result},
                ],
            )

            prompt = prompt["choices"][0]["message"]["content"]

            openai.api_key = config.open_ai_api_key

            response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
            image_url = response["data"][0]["url"]
            image = image_url
        return image

    def add_skill_from_url(self, assistant, url, should_replace=False):
        requirements_names = []

        con = sqlite3.connect("skills.db")

        cur = con.cursor()

        # make sure temp dir exists and is empty
        if not os.path.exists(os.path.join(repos_path, "temp")):
            os.makedirs(f"{repos_path}/temp")
        else:
            rmtree_hard(os.path.join(repos_path, "temp"))
            os.makedirs(f"{repos_path}/temp")

        # clone
        Repo.clone_from(url, f"{repos_path}/temp")

        # get stuff from config
        name = ""
        requirements = []

        with open(f"{repos_path}/temp/config.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
            name = data_loaded["name"] if data_loaded["name"] else uuid.uuid4()
            requirements = (
                data_loaded["requirements"] if "requirements" in data_loaded else []
            )

        # create a temp name
        temp_name = uuid.uuid4()
        os.rename(
            os.path.join(repos_path, "temp"), os.path.join(repos_path, str(temp_name))
        )

        # install other requirements
        updated_requirements = requirements.copy()
        for requirement in requirements:
            req_name = self.add_skill_from_url(assistant, requirement)
            if name != False:
                requirements_names.append(req_name)
            else:
                updated_requirements.remove(requirement)

        prev_action_dict: dict = assistant.action_dict.copy()

        # check if it is already installed
        if os.path.exists(f"{repos_path}/{name}"):
            rmtree_hard(f"{repos_path}/{temp_name}")
            print("Already Installed " + name)
            return False

        print("renaming to final")
        # Save it is name
        os.rename(f"{repos_path}/{temp_name}", f"{repos_path}/{name}")

        # Make sure it is valid
        if not self.is_folder_valid(f"{repos_path}/{name}"):
            print("Not valid")
            rmtree_hard(os.path.join(repos_path, name))
            return False

        # import
        module = importlib.import_module(f"Skills.{name}")

        # Create a settings.yaml
        open(f"{repos_path}/{name}/settings.yaml", "w").close()
        if os.path.exists(f"{repos_path}/{name}/settingsmeta.yaml"):
            with open(f"{repos_path}/{name}/settingsmeta.yaml", "r") as file:
                data = yaml.safe_load(file)
            settings = {}
            for section in data["skillMetadata"]["sections"]:
                for field in section["fields"]:
                    if "name" in field and "value" in field:
                        field_name = field["name"]
                        value = field["value"]
                        if value == "true" or value == "True":
                            value = True
                        elif value == "false" or value == "False":
                            value = False
                        if not isinstance(value, NoneType):
                            settings[field_name] = value
            with open(f"{repos_path}/{name}/settings.yaml", "w") as file:
                yaml.dump(settings, file)
        new_action_dict: dict = {}
        for skill_id, item in assistant.action_dict.items():
            _parameters = tuple(inspect.signature(item["function"]).parameters.items())

            if skill_id not in prev_action_dict:
                new_action_dict[skill_id] = item
                new_action_dict[skill_id]["parameters"] = {}

            assistant.action_dict[skill_id]["parameters"] = (
                assistant.action_dict[skill_id]["parameters"]
                if "parameters" in assistant.action_dict[skill_id]
                else {}
            )

            for argument in _parameters:
                _name = argument[0]
                _type = (
                    f"<{argument[1].annotation}>"
                    if type(argument[1].annotation) is str
                    else f"<{argument[0]}>"
                )
                if skill_id not in prev_action_dict:
                    new_action_dict[skill_id]["parameters"][_name] = _type
                assistant.action_dict[skill_id]["parameters"][_name] = _type
        result = assistant.pm.add_list(new_action_dict, name)
        print(f"NEW:// {new_action_dict}")

        cur.execute(f"DELETE FROM actions WHERE skill='{name}'")

        for action_id, action in result.items():
            cur.execute(
                f"""
            INSERT INTO actions VALUES
                ('{name}', '{action["uuid"]}' ,'{action["id"]}', '{action["name"]}',
                 '{str(action["parameters"]).replace("'", '"')}')
            """
            )

        con.commit()

        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM installedSkills WHERE skill = ?)", (name,)
        )

        # Fetch the result
        result = cur.fetchone()[0]

        if should_replace:
            cur.execute("DELETE FROM installedSkills WHERE skill = ?", (name,))
            cur.execute(
                f"""
                    INSERT INTO installedSkills (skill, version)
                    VALUES ('{name}', 0.0)
            """
            )
        elif not result:
            cur.execute(
                f"""
                    INSERT INTO installedSkills (skill, version)
                    VALUES ('{name}', 0.0)
            """
            )

        con.commit()
        # Put into current memory
        self.add_skill(assistant, name, should_replace=should_replace)
        self.add_requirements_to_db(updated_requirements, requirements_names, name)

        return name

    def add_skill_from_local(self, path, assistant):
        requirements_names = []

        con = sqlite3.connect("skills.db")

        cur = con.cursor()

        # make sure temp dir exists and is empty
        if not os.path.exists(os.path.join(repos_path, "temp")):
            os.makedirs(f"{repos_path}/temp")
        else:
            rmtree_hard(os.path.join(repos_path, "temp"))
            os.makedirs(f"{repos_path}/temp")

        # clone
        shutil.copytree(path, f"{repos_path}/temp")

        # get stuff from config
        name = ""
        requirements = []

        with open(f"{repos_path}/temp/config.yaml", "r") as stream:
            data_loaded = yaml.safe_load(stream)
            name = data_loaded["name"] if data_loaded["name"] else uuid.uuid4()
            requirements = (
                data_loaded["requirements"] if "requirements" in data_loaded else []
            )

        print("renaming to temp")
        # create a temp name
        temp_name = uuid.uuid4()
        os.rename(
            os.path.join(repos_path, "temp"), os.path.join(repos_path, str(temp_name))
        )

        # install other requirements
        updated_requirements = requirements.copy()
        for requirement in requirements:
            req_name = self.add_skill_from_url(assistant, requirement)
            if name != False:
                requirements_names.append(req_name)
            else:
                updated_requirements.remove(requirement)

        prev_action_dict: dict = assistant.action_dict.copy()
        # check if it is already installed
        if os.path.exists(f"{repos_path}/{name}"):
            rmtree_hard(f"{repos_path}/{temp_name}")
            print("Already Installed " + name)
            return False

        # Save it is name
        os.rename(f"{repos_path}/{temp_name}", f"{repos_path}/{name}")

        # Make sure it is valid
        if not self.is_folder_valid(f"{repos_path}/{name}"):
            print("Not valid")
            rmtree_hard(os.path.join(repos_path, name))
            return False

        # import
        module = importlib.import_module(f"Skills.{name}")

        # Create a settings.yaml
        open(f"{repos_path}/{name}/settings.yaml", "w").close()
        if os.path.exists(f"{repos_path}/{name}/settingsmeta.yaml"):
            with open(f"{repos_path}/{name}/settingsmeta.yaml", "r") as file:
                data = yaml.safe_load(file)
            settings = {}
            for section in data["skillMetadata"]["sections"]:
                for field in section["fields"]:
                    if "name" in field and "value" in field:
                        field_name = field["name"]
                        value = field["value"]
                        if value == "true" or value == "True":
                            value = True
                        elif value == "false" or value == "False":
                            value = False
                        if not isinstance(value, NoneType):
                            settings[field_name] = value
            with open(f"{repos_path}/{name}/settings.yaml", "w") as file:
                yaml.dump(settings, file)

        new_action_dict: dict = {}
        for skill_id, item in assistant.action_dict.items():
            _parameters = tuple(inspect.signature(item["function"]).parameters.items())

            if skill_id not in prev_action_dict:
                new_action_dict[skill_id] = item
                new_action_dict[skill_id]["parameters"] = {}

            assistant.action_dict[skill_id]["parameters"] = (
                assistant.action_dict[skill_id]["parameters"]
                if "parameters" in assistant.action_dict[skill_id]
                else {}
            )

            for argument in _parameters:
                _name = argument[0]
                _type = (
                    f"<{argument[1].annotation}>"
                    if type(argument[1].annotation) is str
                    else f"<{argument[0]}>"
                )
                if skill_id not in prev_action_dict:
                    new_action_dict[skill_id]["parameters"][_name] = _type
                assistant.action_dict[skill_id]["parameters"][_name] = _type

        print(f"NEW:// {new_action_dict}")
        result = assistant.pm.add_list(new_action_dict, name)

        cur.execute(f"DELETE FROM actions WHERE skill='{name}'")

        for action_id, action in result.items():
            cur.execute(
                f"""
            INSERT INTO actions VALUES
                ('{name}', '{action["uuid"]}' ,'{action["id"]}', '{action["name"]}',
                '{str(action["parameters"]).replace("'", '"')}')
            """
            )

        con.commit()

        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM installedSkills WHERE skill = ?)", (name,)
        )

        # Fetch the result
        result = cur.fetchone()[0]

        if False:
            cur.execute("DELETE FROM installedSkills WHERE skill = ?", (name,))
            cur.execute(
                f"""
                    INSERT INTO installedSkills (skill, version)
                    VALUES ('{name}', 0.0)
            """
            )
        elif not result:
            cur.execute(
                f"""
                    INSERT INTO installedSkills (skill, version)
                    VALUES ('{name}', 0.0)
            """
            )

        con.commit()
        # Put into current memory
        self.add_skill(assistant, name, False)
        self.add_requirements_to_db(updated_requirements, requirements_names, name)

        return name

    def add_requirements_to_db(self, requirements, requirements_names, skill):
        for i in range(0, len(requirements)):
            url = requirements[i]
            name = requirements_names[i]

            con = sqlite3.connect("skills.db")

            cur = con.cursor()

            cur.execute(
                f"""
                    INSERT INTO requirements (url, name, requiredBy)
                    VALUES ('{url}', '{name}', '{skill}')
            """
            )

            con.commit()

    def is_folder_valid(self, folder_path):
        # Read the config file
        config_file_path = os.path.join(folder_path, "config.yaml")
        with open(config_file_path, "r") as config_file:
            config = yaml.safe_load(config_file)

        # Get the name from the config
        name = config.get("name")

        # Check if the name matches a file in the folder
        file_names = os.listdir(folder_path)
        if f"{name}.py" not in file_names:
            return False

        # Check if the folder contains a class with the same name
        module_file_path = os.path.join(folder_path, f"{name}.py")
        if not os.path.isfile(module_file_path):
            return False

        # Read the file contents
        with open(module_file_path, "r") as module_file:
            file_contents = module_file.read()

        # Check if the class with the same name exists in the file
        if f"class {name}" not in file_contents:
            return False

        # Check if skill is already installed in the database
        conn = sqlite3.connect("skills.db")
        c = conn.cursor()
        value_to_check = name
        c.execute("SELECT COUNT(*) FROM actions WHERE skill = ?", (value_to_check,))
        result = c.fetchone()[0]
        conn.close()
        if result > 0:
            return False

        return True

    def remove_skill(self, skill_name: str, assistant: Assistant):
        if not self.check_if_skill_is_needed(skill_name=skill_name):
            self.remove_from_memory(skill_name, assistant)
            self.remove_from_actions_table(skill_name)
            self.remove_from_installed_skills_table(skill_name)
            self.remove_from_vector_database(skill_name, assistant)
            self.delete_files(skill_name)
            dependancies = self.get_dependancies(skill_name)
            self.remove_from_requirements_table(skill_name)
            self.remove_dependancies(dependancies, assistant)

    def get_dependancies(self, skill_name: str):
        con = sqlite3.connect("skills.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM requirements WHERE requiredBy=?", (skill_name,))
        rows = cur.fetchall()
        return rows

    def remove_from_requirements_table(self, skill_name: str):
        con = sqlite3.connect("skills.db")
        cur = con.cursor()

        cur.execute("DELETE FROM requirements WHERE requiredBy=?", (skill_name,))

        con.commit()

    def remove_dependancies(self, dependancies, assistant):
        for row in dependancies:
            name = row[1]
            self.remove_skill(name, assistant)

    def delete_files(self, skill_name):
        rmtree_hard(os.path.join(repos_path, skill_name))

    def remove_from_memory(self, skill_name: str, assistant: Assistant):
        # reg.all
        reg_copy = reg.all.copy()
        for key, value in reg.all.items():
            if value["skill"].lower() == skill_name.lower():
                del reg_copy[key]

        reg.all = reg_copy

        # action_dict
        action_dict_copy = assistant.action_dict.copy()

        for key, value in assistant.action_dict.items():
            key: str
            skill = key.split(".")[0]

            if skill.lower() == skill_name.lower():
                del action_dict_copy[key]

        assistant.action_dict = action_dict_copy

        # installed_skills
        installed_skills_copy = assistant.installed_skills.copy()

        for key, value in assistant.installed_skills.items():
            key: str
            skill = key

            if skill.lower() == skill_name.lower():
                del installed_skills_copy[key]

        assistant.installed_skills = installed_skills_copy

    def remove_from_actions_table(self, skill_name: str):
        con = sqlite3.connect("skills.db")
        cur = con.cursor()

        cur.execute("DELETE FROM actions WHERE skill=?", (skill_name,))

        con.commit()

    def remove_from_installed_skills_table(self, skill_name: str):
        con = sqlite3.connect("skills.db")
        cur = con.cursor()

        cur.execute("DELETE FROM installedSkills WHERE skill=?", (skill_name,))

        con.commit()

    def remove_from_vector_database(self, skill_name: str, assistant: Assistant):
        assistant.pm.delete(
            {"operator": "Equal", "path": ["skill"], "valueText": skill_name}
        )

    def check_if_skill_is_needed(self, skill_name: str):
        con = sqlite3.connect("skills.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM requirements WHERE name=?", (skill_name,))
        rows = cur.fetchall()

        if len(rows) > 0:
            return True
        else:
            return False

    def get_settings_meta(self, installed_skills):
        data = dict()
        for key, skill in installed_skills.items():
            path = os.path.join(repos_path, skill["name"], "settingsmeta.yaml")
            if os.path.exists(path):
                with open(path, "r") as stream:
                    data_loaded = yaml.safe_load(stream)
                    updated_data = data_loaded.copy()
                    for section_index, section in enumerate(
                        data_loaded["skillMetadata"]["sections"]
                    ):
                        for field_index, field in enumerate(section["fields"]):
                            if "value" in field:
                                if isinstance(field["value"], NoneType):
                                    updated_data["skillMetadata"]["sections"][
                                        section_index
                                    ]["fields"][field_index]["value"] = ""
                            else:
                                updated_data["skillMetadata"]["sections"][
                                    section_index
                                ]["fields"][field_index]["value"] = ""
                            if field["type"] == "checkbox":
                                updated_data["skillMetadata"]["sections"][
                                    section_index
                                ]["fields"][field_index]["parentClasses"] = "form-check"
                                updated_data["skillMetadata"]["sections"][
                                    section_index
                                ]["fields"][field_index][
                                    "inputClasses"
                                ] = "form-check-input"
                                updated_data["skillMetadata"]["sections"][
                                    section_index
                                ]["fields"][field_index][
                                    "labelClasses"
                                ] = "form-check-label"
                            elif field["type"] == "select":
                                options = field["options"].split(";")
                                updated_data["skillMetadata"]["sections"][
                                    section_index
                                ]["fields"][field_index]["options"] = {
                                    option.split("|")[0]: option.split("|")[1]
                                    for option in options
                                }

                            else:
                                updated_data["skillMetadata"]["sections"][
                                    section_index
                                ]["fields"][field_index]["parentClasses"] = ""
                                updated_data["skillMetadata"]["sections"][
                                    section_index
                                ]["fields"][field_index][
                                    "inputClasses"
                                ] = "form-control"
                                updated_data["skillMetadata"]["sections"][
                                    section_index
                                ]["fields"][field_index]["labelClasses"] = ""
            else:
                data_loaded = None
            if data_loaded:
                data[skill["name"]] = data_loaded
        return data
