import os
import json

class ConfigService:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.config = {}
            self.save_config()
        else:
            with open(self.config_file, 'r') as f:
                try:
                    self.config = json.load(f)
                except json.JSONDecodeError:
                    self.config = {}
                    self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_api_key(self):
        return self.config.get('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))

    def set_api_key(self, api_key):
        self.config['OPENAI_API_KEY'] = api_key
        self.save_config()
