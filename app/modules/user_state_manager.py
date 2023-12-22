import json
from typing import Dict

class UserStateManager:
    def __init__(self, data_file_path: str):
        self.data_file_path = data_file_path
        self.user_data: Dict[int, Dict] = self.load_user_data()

    def load_user_data(self):
        try:
            with open(self.data_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_user_data(self):
        with open(self.data_file_path, 'w') as file:
            json.dump(self.user_data, file)

    def get_user_data(self, user_id):
        return self.user_data.get(user_id, {})

    def set_user_data(self, user_id, data):
        self.user_data[user_id] = data
        self.save_user_data()

    def clear_user_data(self, user_id):
        if user_id in self.user_data:
            del self.user_data[user_id]
            self.save_user_data()
            
# Usage example:
data_file_path = "user_data.json"
user_state_manager = UserStateManager(data_file_path)

# Access user data
user_id = 123
user_data = user_state_manager.get_user_data(user_id)

# Modify user data
user_data['step'] = 1
user_state_manager.set_user_data(user_id, user_data)

# Clear user data
user_state_manager.clear_user_data(user_id)