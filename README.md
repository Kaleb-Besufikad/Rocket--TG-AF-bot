# PyWardBot

> Telegram forwarder written in Python

PyWardBot is an open source Telegram message forwarder powered by
[Pyrogram](https://github.com/pyrogram/pyrogram)

## Features

- Schedule messages
- Send messages to multiple channels
- record interaction history and allow interaction on recorded message
- load and schedule messages after server restarts

## Use cases

- Contiinuously send messages to specified channels

## Installation and configuration

### Installation

First, you will need to have
[Python](https://realpython.com/installing-python/#how-to-install-python-on-windows) installed on your system.

Also you will need to create a new
[Telegram bot](https://www.siteguarding.com/en/how-to-get-telegram-bot-api-token) on @Bot_father
and get the bot token.

After installing Python and creating a bot, open a terminal and do the following:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python3 app/main.py
```

Once you have installed the dependencies, you will need to make the following changes:

- edit the `/app/config/users.json` file with your own list of `api_id` and `api_hash` values in order to run the allow user.
- edit the `/app/config/bot.json` file with the `bot_token` you got from Telegram.
- edit the `/app/mocules/constants.py` file. on the first line, include all channels you want to target inside the list, `TARGET_CHANNELS`.

### Configuration

After running the bot for the first time, you will get the following output:

```
01-01-2024 19:09:18 - user_client:35 - INFO: Bot [<USER 1>] configured
01-01-2024 19:09:18 - user_client:35 - INFO: Bot [<USER 2>] configured
01-01-2024 19:09:18 - main:42 - INFO: BOT @<BOT TOKEN> configured
01-01-2024 19:09:18 - main:47 - INFO: Log-in with your bot token
01-01-2024 19:09:22 - main:49 - INFO: Bot started
01-01-2024 19:09:22 - main:50 - INFO: Bot username: @<BOT NAME>
01-01-2024 19:09:22 - main:54 - INFO: Log-in with your phone number
```

[CHECKPOINT] You will be prompted to enter your phone number:

```bash
25-05-2022 18:00:00 - main:839 - INFO: Log-in with your phone number
Welcome to Pyrogram (version 1.4.8)
Pyrogram is free software and comes with ABSOLUTELY NO WARRANTY. Licensed
under the terms of the GNU Lesser General Public License v3 or later (LGPLv3+).

Enter phone number or bot token:
```

Remember to enter your phone number in the international format (e.g. +251912345678).

After entering your phone number, a code will be sent to your Telegram account. Enter the code and press enter.

Repeat the process starting from [CHECKPOINT] for the number oof accounts you registered in users.json

## FAQ🚧

under construction🏗️
