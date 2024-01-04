# TODO: whitelist words or whitelist patterns to only capture messages that
# match with a pattern or contains a word.
# TODO: make a filter config to only capture messages that contains selected
# media. Ex: Select to only forward messages with photos, videos, audios, etc.
# TODO: Blacklist regex pattern?
# TODO: Make a filter to only capture types of messages.
# Ex: Only forwarded messages, edited messages, deleted messages, etc.
# TODO: Make a filter to only send media messages, skipping text and viceversa
# Ex: If a photo with a caption is sent, only send the photo, not the caption
# TODO: Toggle message removal from the chat.
# TODO: Edited, deleted, pinned, replied messages toggles.

from pathlib import Path
from typing import List
from cv2 import imread
from pyrogram import Client

from modules import Bot, logger
# Config path
app_dir = Path(__file__).parent.parent
config_dir = app_dir / "config"
# Load the bot configuration
user_configs = Bot().get_user_config()
users: List[Client] = []
for user_config in user_configs:
    # NAME= bot_config['name']
    API_ID = user_config["api_id"]
    API_HASH = user_config["api_hash"]
    users.append(Client(
        str(Path(config_dir/f"user{API_ID}")),
        api_id=API_ID,
        api_hash=API_HASH,
        # bot_token=''
    ))
    logger.info(f"Bot [{API_ID}] configured")
