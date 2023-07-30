from Config import Config
import requests

config = Config()


def get_sentament(message):
    try:
        API_URL = "https://api-inference.huggingface.co/models/SamLowe/roberta-base-go_emotions"
        headers = {"Authorization": f"Bearer {config['HUGGINGFACE_API_KEY']}"}

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()

        output = query(
            {
                "inputs": message,
            }
        )

        return output[0][0]["label"]
    except:
        return "neutral"
