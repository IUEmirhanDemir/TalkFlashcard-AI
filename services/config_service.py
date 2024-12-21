import os
import json

class ConfigService:
    """
    Service for managing configuration settings for the application.
    Handles loading, saving, and retrieving configurations from a JSON file.
    """

    def __init__(self, config_file='config.json'):
        """
        Initializes the configuration service with the specified configuration file.

        Args:
            config_file (str): The name of the configuration file. Defaults to 'config.json'.
        """
        self.config_file = config_file  # File where configuration is stored
        self.config = {}  # Dictionary to hold configuration data
        self.load_config()  # Load the configuration when the service is initialized

    def load_config(self):
        """
        Loads the configuration from the specified JSON file.
        If the file does not exist or is invalid, creates a new configuration.
        """
        if not os.path.exists(self.config_file):
            self.config = {}  # Initialize with an empty config if file is missing
            self.save_config()  # Save the empty config
        else:
            with open(self.config_file, 'r') as f:
                try:
                    self.config = json.load(f)  # Load config from file
                except json.JSONDecodeError:
                    # Handle corrupted or invalid JSON file
                    self.config = {}
                    self.save_config()  # Save a fresh empty config

    def save_config(self):
        """
        Saves the current configuration to the specified JSON file.
        """
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)  # Save the configuration with 4-space indentation

    def get_api_key(self):
        """
        Retrieves the OpenAI API key from the configuration file or environment variables.

        Returns:
            str or None: The API key if found, otherwise None.
        """
        return self.config.get('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))

    def set_api_key(self, api_key):
        """
        Updates the OpenAI API key in the configuration file.

        Args:
            api_key (str): The new API key to be saved.
        """
        self.config['OPENAI_API_KEY'] = api_key  # Set the API key in the configuration dictionary
        self.save_config()  # Save the updated configuration
