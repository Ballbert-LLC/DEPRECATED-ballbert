from transformers import pipeline


def get_sentament(message):
    sentiment_pipeline = pipeline(
        "sentiment-analysis", model="SamLowe/roberta-base-go_emotions"
    )

    data = [message]
    return sentiment_pipeline(data)[0]["label"]
