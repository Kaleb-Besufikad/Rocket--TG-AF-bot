import json
import os
from pathlib import Path

from modules import logger

# Create a folder that will hold the configuration files
app_dir = Path(__file__).parent.parent
config_dir = app_dir / "config"
config_dir.mkdir(exist_ok=True)


class Bot:
    bot = {
        "admins": [67821136878, 26871378216],
        "api_id": 63721832,
        "api_hash": "nfljawekn2873913hkjhqnedsa",
        "bot_token": "678321876231:qoguw87xynow8q7nyr"
    }

    user = [{
        "api_id": "123456",
        "api_hash": "hkdjhlaskjdfh872938079341hjhksjdfsfa"
    }]

    def get_config(self) -> dict:
        """Load the bot configuration from the bot.json file."""
        if not os.path.exists(config_dir/"bot.json"):
            logger.error("bot.json not found")
            logger.warning("bot.json has been created with default values. " +
                           "Please edit it with your own api_id and api_hash" +
                           " values. You can find/create them on " +
                           "https://my.telegram.org/apps")

            with open(config_dir/"bot.json", "w") as f:
                json.dump(self.bot, f, indent=4, ensure_ascii=False)
            exit(1)

        with open(config_dir/"test_bot.json", "r") as f:
            return json.load(f)
            # load= json.load(f)
            # return load

    def get_user_config(self) -> dict:
        """Load the bot configuration from the users.json file."""
        if not os.path.exists(config_dir/"users.json"):
            logger.error("users.json not found")
            logger.warning("users.json has been created with default values. " +
                           "Please edit it with your own api_id and api_hash" +
                           " values. You can find/create them on " +
                           "https://my.telegram.org/apps")

            with open(config_dir/"users.json", "w") as f:
                json.dump(self.user, f, indent=4, ensure_ascii=False)
            # exit(1)

        with open(config_dir/"test_users.json", "r") as f:
            return json.load(f)
            # load= json.load(f)
            # return load

    def add_admin(self, admin: int) -> None:
        """Add an admin to the bot configuration."""
        bot = self.get_config()
        if admin not in bot["admins"]:
            bot["admins"].append(admin)

            with open(config_dir/"bot.json", "w") as f:
                json.dump(bot, f, indent=4, ensure_ascii=False)
