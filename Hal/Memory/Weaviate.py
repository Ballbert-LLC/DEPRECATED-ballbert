import json
import time
import weaviate
from colorama import Fore, Style

from Config import Config

config = Config()


class Weaviate:
    def __init__(self):
        self.client = weaviate.Client(
            url="http://localhost:8080",  # Replace with your endpoint
        )
        self.vec_num = 0
        self.class_obj = {
            "class": "Action",
            # description of the class
            "description": "Action that can be used in a voice assistant",
            "properties": [
                {
                    "dataType": ["text"],
                    "description": "The name",
                    "name": "name",
                },
                {
                    "dataType": ["text"],
                    "description": "The identifier",
                    "name": "identifier",
                },
                {
                    "dataType": ["text"],
                    "description": "The skill the action is from",
                    "name": "skill",
                },
                {
                    "dataType": ["text[]"],
                    "description": "A list of parameters",
                    "name": "parameters",
                },
            ],
            "vectorizer": "text2vec-openai",
        }

        if not self.client.schema.contains(self.class_obj):
            self.client.schema.create_class(self.class_obj)
        else:
            if config["SETUP_MODE"]:
                self.client.schema.delete_class("Action")
                self.client.schema.create_class(self.class_obj)

    def add_list(self, datas: list, skill_name):
        results = datas.copy()
        with self.client.batch(
            batch_size=100, weaviate_error_retries=weaviate.WeaviateErrorRetryConf()
        ) as batch:
            for skill_id, data in datas.items():
                properties = {
                    "name": data["name"],
                    "identifier": data["id"],
                    "skill": skill_name,
                    "parameters": [
                        f"{i}: {item.get('description')}"
                        for i, item in data["parameters"].items()
                    ],
                }

                results[data["id"]]["uuid"] = self.client.batch.add_data_object(
                    properties, "Action"
                )

                time.sleep(0.1)
        return results

    def get(self, data):
        return self.get_relevant(data, 1)

    def clear(self):
        self.client.schema.delete_all()  # deletes all classes along with the whole data
        return "Obliviated"

    def get_relevant(self, data, num_relevant=5):
        """
        Returns all the data in the memory that is relevant to the given data.
        :param data: The data to compare to.
        :param num_relevant: The number of relevant data to return. Defaults to 5
        """
        result = (
            self.client.query.get("Action", ["name", "identifier", "parameters"])
            .with_near_text({"concepts": [str(data)]})
            .with_limit(num_relevant)
            .do()
        )

        return [item["identifier"] for item in result["data"]["Get"]["Action"]]

    def get_stats(self):
        return self.client.schema()

    def delete(self, where={}):
        # default QUORUM
        self.client.batch.consistency_level = (
            weaviate.data.replication.ConsistencyLevel.ALL
        )

        result = self.client.batch.delete_objects(
            class_name="Action",
            # same where operator as in the GraphQL API
            where=where,
            output="verbose",
            dry_run=False,
        )
        return result
