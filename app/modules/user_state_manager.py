import json
import os
from pathlib import Path
from typing import Dict

from modules.logger import logger


class UserStateManager:
    def __init__(self, data_file_path: Path):
        self.data_file_path = data_file_path
        self.user_data: Dict[int, Dict] = self.load_user_data()
        logger.info(
            f"Loaded user data for {len(self.user_data.keys())} users.")

    def load_user_data(self):
        if not os.path.exists(self.data_file_path):
            logger.error(f'File not found: {self.data_file_path}')
            logger.error(f'Creating: {self.data_file_path}')
            with open(self.data_file_path, 'w')as file:
                json.dump({}, file, indent=4, ensure_ascii=False)
            return {}

        logger.info("Loading user data. . .")
        with open(self.data_file_path, 'r') as file:
            content = json.load(file)
            if not content:
                with open(self.data_file_path, 'w') as file:
                    json.dump({}, file, indent=4, ensure_ascii=False)
                content = {}
            return content

    def save_user_data(self):
        with open(self.data_file_path, 'w') as file:
            json.dump(self.user_data, file)

    def get_user_data(self, user_id):
        return self.user_data.get(user_id, {})

    def set_user_data(self, user_id, data):
        self.user_data[user_id] = data
        self.save_user_data()
        logger.info(f"user {user_id} updated with data: {data}")

    def clear_user_data(self, user_id):
        if user_id in self.user_data:
            del self.user_data[user_id]
            self.save_user_data()

# Usage example:
# data_file_path = "user_data.json"
# user_state_manager = UserStateManager(data_file_path)

# # Access user data
# user_id = 123
# user_data = user_state_manager.get_user_data(user_id)

# # Modify user data
# user_data['step'] = 1
# user_state_manager.set_user_data(user_id, user_data)

# # Clear user data
# user_state_manager.clear_user_data(user_id)
