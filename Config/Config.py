import os
import dotenv


class Config:
    def __init__(self, dotenv_path="./.env"):
        if not os.path.exists(dotenv_path):
            open(dotenv_path, "w").close()
        self.populate_values()
        self.dotenv_path = dotenv_path

    def __getitem__(self, key):
        self.populate_values()
        return self.data[key]

    def __setitem__(self, key, value):
        dotenv.set_key(self.dotenv_path, str(key), str(value))
        dotenv.load_dotenv()
        self.populate_values()
        self.data[key] = value

    def populate_values(self):
        data = dict(dotenv.dotenv_values())
        for key, value in data.items():
            if value == "True":
                data[key] = True
            elif value == "False":
                data[key] = False
            try:
                num = float(value)
                data[key] = num
            except ValueError:
                pass
            try:
                num = int(value)
                data[key] = num
            except ValueError:
                pass
        self.data = data

    def __delitem__(self, key):
        self.populate_values()
        del self.data[key]

    def __contains__(self, key):
        self.populate_values()
        return key in self.data

    def __len__(self):
        self.populate_values()
        return len(self.data)

    def __str__(self):
        self.populate_values()
        return str(self.data)

    def keys(self):
        self.populate_values()
        return self.data.keys()

    def values(self):
        self.populate_values()
        return self.data.values()

    def items(self):
        self.populate_values()
        return self.data.items()
