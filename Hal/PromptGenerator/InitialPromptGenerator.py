""" A module for generating custom prompt strings."""
from __future__ import annotations

import json
from typing import Any

from Config import Config

config = Config()


class InitialPromptGenerator:
    """
    A class for generating custom prompt strings based on constraints, commands,
        resources, and performance evaluations.
    """

    def __init__(self) -> None:
        """
        Initialize the PromptGenerator object with empty lists of constraints,
            commands, resources, and performance evaluations.
        """
        self.constraints = []
        self.commands = []
        self.resources = []
        self.performance_evaluation = []
        self.response_format = {
            # "feedback": "feedback that can be used to improve your response next time",
            "command": {"name": "command name", "args": {"arg name": "value"}},
        }

    def add_constraint(self, constraint: str) -> None:
        """
        Add a constraint to the constraints list.

        Args:
            constraint (str): The constraint to be added.
        """
        self.constraints.append(constraint)

    def add_command(self, command_label: str, command_name: str, args=None) -> None:
        """
        Add a command to the commands list with a label, name, and optional arguments.

        Args:
            command_label (str): The label of the command.
            command_name (str): The name of the command.
            args (dict, optional): A dictionary containing argument names and their
              values. Defaults to None.
        """
        if args is None:
            args = {}

        command_args = {arg_key: arg_value for arg_key,
                        arg_value in args.items()}

        command = {
            "label": command_label,
            "name": command_name,
            "args": command_args,
        }

        self.commands.append(command)

    def _generate_command_string(self, command: dict[str, Any]) -> str:
        """
        Generate a formatted string representation of a command.

        Args:
            command (dict): A dictionary containing command information.

        Returns:
            str: The formatted command string.
        """
        args_string = ", ".join(
            f'"{key}": "{value}"' for key, value in command["args"].items()
        )
        return f'{command["label"]}: "{command["name"]}", args: {args_string}'

    def add_resource(self, resource: str) -> None:
        """
        Add a resource to the resources list.

        Args:
            resource (str): The resource to be added.
        """
        self.resources.append(resource)

    def add_performance_evaluation(self, evaluation: str) -> None:
        """
        Add a performance evaluation item to the performance_evaluation list.

        Args:
            evaluation (str): The evaluation item to be added.
        """
        self.performance_evaluation.append(evaluation)

    def _generate_numbered_list(self, items: list[Any], item_type="list") -> str:
        """
        Generate a numbered list from given items based on the item_type.

        Args:
            items (list): A list of items to be numbered.
            item_type (str, optional): The type of items in the list.
                Defaults to 'list'.

        Returns:
            str: The formatted numbered list.
        """
        if item_type == "command":
            return "\n".join(
                f"{i+1}. {self._generate_command_string(item)}"
                for i, item in enumerate(items)
            )
        else:
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))

    def _generate_prompt_string(self) -> str:
        """
        Generate a prompt string based on the constraints, commands, resources,
            and performance evaluations.

        Returns:
            str: The generated prompt string.
        """
        formatted_response_format = "🖥️" + \
            json.dumps(self.response_format, indent=4)
        return (
            f"Constraints:\n{self._generate_numbered_list(self.constraints)}\n\n"
            "Commands:\n"
            f"{self._generate_numbered_list(self.commands, item_type='command')}\n\n"
            f"Resources:\n{self._generate_numbered_list(self.resources)}\n\n"
            "Performance Evaluation:\n"
            f"{self._generate_numbered_list(self.performance_evaluation)}\n\n"
            "You should only respond in JSON format as described below \nResponse"
            f" Format: \n{formatted_response_format} \nEnsure the response can be"
            " parsed by Python json.loads"
        )

    def contruct_init_prompt(self) -> str:
        """
        Returns a prompt to the user with the class information in an organized fashion.
        Parameters:
            None
        Returns:
            full_prompt (str): A string containing the initial prompt for the user
                including the ai_name, ai_role and ai_goals.
        """

        prompt_start = (
            "Your decisions must try to be made independently without"
            " seeking user assistance. Play to your strengths as an LLM and pursue"
            " simple strategies with no legal complications."
            ""
        )

        # Construct full prompt
        full_prompt = (
            f"You are {config.name}, {config.role}\n{prompt_start}"
        )

        full_prompt += f"\n\n{self._generate_prompt_string()}"
        return full_prompt
