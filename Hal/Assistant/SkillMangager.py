import openai
import inspect
import shutil
import sqlite3
import uuid

import yaml
from git import Repo
import importlib
from ..Decorators import paramRegistrar, reg

import os
from Config import Config
from ..Utils import rmtree_hard

config = Config()

repos_path = f"{os.path.abspath(os.getcwd())}/Skills"


class SkillMangager():

    def __init__(self) -> None:
        pass

    def add_skill(self, assistant, skill, should_replace=True):
        con = sqlite3.connect("skills.db")

        cur = con.cursor()

        prev_action_dict = assistant.action_dict.copy()

        importlib.import_module(f'Skills.{skill}')

        new_action_dict: dict = {}

        # Adds into attributes
        action_dict: dict = reg.all

        for skill_id, item in action_dict.items():

            _parameters = tuple(inspect.signature(
                item["function"]).parameters.items())

            if skill_id not in prev_action_dict:
                new_action_dict[skill_id] = item
                new_action_dict[skill_id]["parameters"] = {}

            action_dict[skill_id]["parameters"] = action_dict[skill_id]["parameters"] if "parameters" in action_dict[skill_id] else {}

            for argument in _parameters:
                _name = argument[0]
                _type = f"<{argument[1].annotation}>" if type(
                    argument[1].annotation) is str else f"<{argument[0]}>"
                if skill_id not in prev_action_dict:
                    new_action_dict[skill_id]["parameters"][_name] = _type
                action_dict[skill_id]["parameters"][_name] = _type

        actions: list[tuple] = [(item["name"], item["id"], item["parameters"])
                                for skill_id, item in reg.all.items()]

        # Adds into attributes

        con.commit()

        def get_image_url():
            if os.path.exists(os.path.join(repos_path, skill, "icon.png")):
                image = os.path.join(repos_path, skill, "icon.png")
            else:
                res = ""

                description = res or None

                with open(f"{repos_path}/{skill}/config.yaml", 'r') as stream:
                    data_loaded = yaml.safe_load(stream)
                    name = data_loaded["name"]
                    description = data_loaded["description"] if "description" in data_loaded else "No description provided"

                # Open a connection to the database file
                conn = sqlite3.connect('skills.db')

                # Create a cursor object to execute SQL commands
                cursor = conn.cursor()

                # Execute a SELECT query on the actions table
                cursor.execute("SELECT * FROM actions WHERE skill = ?",
                               (name,))

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
                        {"role": "system", "content": "You are a prompt generator for an image generator that. Your prompts are made to be an turn into an icon for a skill addon with the details in the paramiters the user provides. Constraints: Speak in language that an image generator could understand."},
                        {"role": "user", "content": result},
                    ]
                )

                prompt = prompt["choices"][0]["message"]["content"]

                openai.api_key = config.open_ai_api_key

                response = openai.Image.create(
                    prompt=prompt,
                    n=1,
                    size="1024x1024"
                )
                image_url = response['data'][0]['url']
                image = image_url
            return image

        image = get_image_url()

        # ALL Image suff

        assistant.installed_skills.append(
            {"image": image, "name": skill, "version": 0.0})

        assistant.action_dict = action_dict
        assistant.actions = actions
        assistant.action_functions = {key: value["function"]
                                      for key, value in assistant.action_dict.items()}

    def add_skill_from_url(self, assistant, url, should_replace=False):
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

        with open(f"{repos_path}/temp/config.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            name = data_loaded["name"] if data_loaded["name"] else uuid.uuid4()
            requirements = data_loaded["requirements"] if "requirements" in data_loaded else [
            ]

        # create a temp name
        temp_name = uuid.uuid4()
        os.rename(os.path.join(repos_path, "temp"),
                  os.path.join(repos_path, str(temp_name)))

        # install other requirements
        for requirement in requirements:
            self.add_skill_from_url(assistant, requirement)

        prev_action_dict: dict = assistant.action_dict.copy()

        # check if it is already installed
        if os.path.exists(f"{repos_path}/{name}"):
            rmtree_hard(f"{repos_path}/{temp_name}")
            print("Already Installed")
            return False

        # Save it is name
        os.rename(f"{repos_path}/{temp_name}", f"{repos_path}/{name}")

        # Make sure it is valid
        if not self.is_folder_valid(f"{repos_path}/{name}"):
            print("Not valid")
            rmtree_hard(os.path.join(repos_path, name))
            return False

        # Create a settings.yaml
        open(f"{repos_path}/{name}/settings.yaml", 'w').close()

        new_action_dict: dict = {}

        for skill_id, item in assistant.action_dict.items():

            _parameters = tuple(inspect.signature(
                item["function"]).parameters.items())

            if skill_id not in prev_action_dict:
                new_action_dict[skill_id] = item
                new_action_dict[skill_id]["parameters"] = {}

            assistant.action_dict[skill_id]["parameters"] = assistant.action_dict[skill_id][
                "parameters"] if "parameters" in assistant.action_dict[skill_id] else {}

            for argument in _parameters:
                _name = argument[0]
                _type = f"<{argument[1].annotation}>" if type(
                    argument[1].annotation) is str else f"<{argument[0]}>"
                if skill_id not in prev_action_dict:
                    new_action_dict[skill_id]["parameters"][_name] = _type
                assistant.action_dict[skill_id]["parameters"][_name] = _type

        result = assistant.pm.add_list(new_action_dict)

        cur.execute(f"DELETE FROM actions WHERE skill='{name}'")

        for action_id, action in result.items():
            cur.execute(f"""
            INSERT INTO actions VALUES
                ('{name}', '{action["uuid"]}' ,'{action["id"]}', '{action["name"]}', '{str(action["parameters"]).replace("'", '"')}')
            """)

        con.commit()

        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM installedSkills WHERE skill = ?)", (name,))

        # Fetch the result
        result = cur.fetchone()[0]

        if should_replace:
            cur.execute("DELETE FROM installedSkills WHERE skill = ?",
                        (name,))
            cur.execute(f"""
                    INSERT INTO installedSkills (skill, version)
                    VALUES ('{name}', 0.0)
            """)
        elif not result:
            cur.execute(f"""
                    INSERT INTO installedSkills (skill, version)
                    VALUES ('{name}', 0.0)
            """)

        con.commit()
        # Put into current memory
        self.add_skill(assistant, name, should_replace=should_replace)

        return True

    def is_folder_valid(self, folder_path):

        # Read the config file
        config_file_path = os.path.join(folder_path, 'config.yaml')
        with open(config_file_path, 'r') as config_file:
            config = yaml.safe_load(config_file)

        # Get the name from the config
        name = config.get('name')

        # Check if the name matches a file in the folder
        file_names = os.listdir(folder_path)
        if f"{name}.py" not in file_names:
            return False

        # Check if the folder contains a class with the same name
        module_name = name
        module_path = os.path.join(folder_path, f"{module_name}.py")
        if not os.path.isfile(module_path):
            return False
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, name):
            return False

        # Check if skill is already installed in the databse
        conn = sqlite3.connect('skills.db')
        c = conn.cursor()
        value_to_check = name
        c.execute("SELECT COUNT(*) FROM actions WHERE skill = ?",
                  (value_to_check,))
        result = c.fetchone()[0]
        conn.close()
        if result > 0:
            return False

        return True
