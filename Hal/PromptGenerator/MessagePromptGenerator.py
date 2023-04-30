import json
import time

from openai.error import RateLimitError
from ..Classes import Response

from ..Config import Config
from ..PromptGenerator import InitialPromptGenerator
from ..TokenCounter import count_message_tokens, num_tokens
from ..Utils import create_chat_completion

config = Config()


def create_chat_message(role, content):
    """
    Create a chat message with the given role and content.

    Args:
    role (str): The role of the message sender, e.g., "system", "user", or "assistant".
    content (str): The content of the message.

    Returns:
    dict: A dictionary containing the role and content of the message.
    """
    return {"role": role, "content": content}


def create_response_message(name, content):
    if isinstance(content, Response):
        data = content.data
    else:
        data = None
    if data:
        return f"From Backend: The result of {name} is {data}"
    else:
        return f"From Backend: There was an error do not retry"


def get_prompt_gerarator(user_input):
    """
    This function generates a prompt string that includes various constraints,
        commands, resources, and performance evaluations.

    Returns:
        str: The generated prompt string.
    """

    from Hal import assistant

    # Initialize the Config object
    # Initialize the PromptGenerator object
    prompt_generator = InitialPromptGenerator()

    prompt_generator.add_constraint("No user assistance")
    prompt_generator.add_constraint(
        'Exclusively use the commands listed in double quotes e.g. "command name"'
    )
    prompt_generator.add_constraint(
        'Only output in the specified JSON format'
    )
    prompt_generator.add_constraint(
        'Only output with the commands'
    )
    prompt_generator.add_constraint(
        "All times when you use a command you should start the whole statement with a 🖥️"
    )
    prompt_generator.add_constraint(
        'Only use commands that are listed in the command list'
    )
    prompt_generator.add_constraint(
        'When provided with the result of a command you should share the result with the user'
    )

    prompt_generator.add_constraint(
        'Follow other constraints'
    )

    # Define the command list
    dict_commands = assistant.pm.get_relevant(user_input, num_relevant=10)

    commands = []

    for action in dict_commands:
        name = action["name"]
        identifier = action["identifier"]
        parameters = {}

        for param in action["parameters"]:
            for key, value in json.loads(param.replace("'", '"')).items():
                parameters[key] = value

        commands.append((name, identifier, parameters))

    # Add commands to the PromptGenerator object
    for command_label, command_name, args in commands:
        prompt_generator.add_command(command_label, command_name, args)

    prompt_generator.add_command("Do Nothing", "system.do_nothing", args=None)
    prompt_generator.add_command(
        "Speak result to user", "system.speak", args={"speach": "<string>"})

    # Add resources to the PromptGenerator object
    prompt_generator.add_resource(
        "Taking multiple turns the with the output of the command provided as the next input."
    )

    prompt_generator.add_resource(
        "The result of a command will be said to you in the format Result of ... is ..."
    )

    # Add performance evaluations to the PromptGenerator object
    prompt_generator.add_performance_evaluation(
        "Continuously review and analyze your actions to ensure you are performing to"
        " the best of your abilities."
    )
    prompt_generator.add_performance_evaluation(
        "Constructively self-criticize your big-picture behavior constantly."
    )
    prompt_generator.add_performance_evaluation(
        "Reflect on past decisions and strategies to refine your approach."
    )
    prompt_generator.add_performance_evaluation(
        "Every command has a cost, so be smart and efficient. Aim to complete tasks in"
        " the least number of steps."
    )
    prompt_generator.add_performance_evaluation(
        "Only output in specified json format"
    )
    prompt_generator.add_performance_evaluation(
        "Followed all contraints"
    )

    # Generate the prompt string
    return prompt_generator


def generate_context(prompt, full_message_history, model):
    current_context = [
        create_chat_message("system", prompt),
        create_chat_message(
            "system", f"The current time and date is {time.strftime('%c')}"
        ),
    ]

    # Add messages from the full message history until we reach the token limit
    next_message_to_add_index = len(full_message_history) - 1
    insertion_index = len(current_context)
    # Count the currently used tokens

    current_tokens_used = count_message_tokens(current_context, model)
    return (
        next_message_to_add_index,
        current_tokens_used,
        insertion_index,
        current_context,
    )


# TODO: Change debug from hardcode to argument
def chat_with_ai(
    user_input, full_message_history, token_limit
):
    """Interact with the OpenAI API, sending the prompt, user input, message history,
    and permanent memory."""

    prompt = get_prompt_gerarator(user_input=user_input).contruct_init_prompt()

    while True:
        try:
            """
            Interact with the OpenAI API, sending the prompt, user input,
                message history, and permanent memory.

            Args:
                prompt (str): The prompt explaining the rules to the AI.
                user_input (str): The input from the user.
                full_message_history (list): The list of all messages sent between the
                    user and the AI.
                permanent_memory (Obj): The memory object containing the permanent
                  memory.
                token_limit (int): The maximum number of tokens allowed in the API call.

            Returns:
            str: The AI's response.
            """
            model = config.llm  # TODO: Change model from hardcode to argument
            # Reserve 1000 tokens for the response

            send_token_limit = token_limit - 1000

            # relevant_memory = (
            #     ""
            #     if len(full_message_history) == 0
            #     else permanent_memory.get_relevant(str(full_message_history[-9:]), 10)
            # )

            # print(f"Memory Stats: {permanent_memory.get_stats()}")

            (
                next_message_to_add_index,
                current_tokens_used,
                insertion_index,
                current_context,
            ) = generate_context(prompt, full_message_history, model)

            while current_tokens_used > 2500:
                # remove memories until we are under 2500 tokens
                relevant_memory = relevant_memory[:-1]
                (
                    next_message_to_add_index,
                    current_tokens_used,
                    insertion_index,
                    current_context,
                ) = generate_context(
                    prompt, relevant_memory, full_message_history, model
                )

            current_tokens_used += count_message_tokens(
                [create_chat_message("user", user_input)], model
            )  # Account for user input (appended later)

            while next_message_to_add_index >= 0:
                # print (f"CURRENT TOKENS USED: {current_tokens_used}")
                message_to_add = full_message_history[next_message_to_add_index]
                tokens_to_add = count_message_tokens(
                    [message_to_add], model
                )
                if current_tokens_used + tokens_to_add > send_token_limit:
                    break

                # Add the most recent message to the start of the current context,
                #  after the two system prompts.
                current_context.insert(
                    insertion_index, full_message_history[next_message_to_add_index]
                )

                # Count the currently used tokens
                current_tokens_used += tokens_to_add

                # Move to the next most recent message in the full message history
                next_message_to_add_index -= 1

            # Append user input, the length of this is accounted for above
            current_context.extend([create_chat_message("user", user_input)])

            # Calculate remaining tokens
            tokens_remaining = token_limit - current_tokens_used
            # assert tokens_remaining >= 0, "Tokens remaining is negative.
            # This should never happen, please submit a bug report at
            #  https://www.github.com/Torantulino/Auto-GPT"

            # Debug print the current context
            if config.debug_mode:
                print(f"Token limit: {token_limit}")
                print(f"Send Token Count: {current_tokens_used}")
                print(f"Tokens remaining for response: {tokens_remaining}")

            # TODO: use a model defined elsewhere, so that model can contain
            # temperature and other settings we care about
            return current_context

            # assistant_reply = create_chat_completion(
            #     model=model,
            #     messages=current_context,
            #     max_tokens=tokens_remaining,
            # )

            # # Update full message history
            # full_message_history.append(create_chat_message("user", user_input))
            # full_message_history.append(
            #     create_chat_message("assistant", assistant_reply)
            # )

            # return assistant_reply
        except RateLimitError:
            # TODO: When we switch to langchain, this is built in
            print("Error: ", "API Rate Limit Reached. Waiting 10 seconds...")
            time.sleep(10)
