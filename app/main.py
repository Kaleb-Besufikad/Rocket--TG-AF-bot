import datetime
import json
from os import truncate
import os
from pathlib import Path
from random import randint
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pyrogram import Client, filters, idle
from pyrogram.types import (Message, CallbackQuery)

from modules import (
    get_keyboard,
    UserStateManager,
    Bot,
    TARGET_CHANNELS,
    INPUT_STATES,
    COMMANDS,
    users,
    logger,
    save_jobs_to_file,
    send_message_job
)
# from logger import logger

# Config path
app_dir = Path(__file__).parent
config_dir = app_dir / "config"

# Load the bot configuration
bot_config = Bot().get_config()
API_ID = bot_config["api_id"]
API_HASH = bot_config["api_hash"]
TOKEN = bot_config["bot_token"]
bot = Client(
    str(Path(config_dir/f"bot{TOKEN}")),
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN
)
logger.info(f"BOT @{TOKEN} configured")
scheduler = AsyncIOScheduler()


if not Path(config_dir/f"bot{bot.api_id}.session").exists():
    logger.info("Log-in with your bot token")
bot.start()
logger.info("Bot started")
logger.info(f"Bot username: @{bot.get_me().username}")

for user in users:
    if not Path(config_dir/f"user{user.api_id}.session").exists():
        logger.info("Log-in with your phone number")
    user.start()
    # Iter over all chats
    for dialog in user.get_dialogs():
        pass
    Bot().add_admin(user.get_me().id)  # Add user id to admin database
    logger.info(f"User added")
    logger.info(f"User: @{user.get_me().username}")
user_data = UserStateManager(config_dir/"user_answers.json")


async def is_admin(filter, client: Client, event: Message | CallbackQuery):
    """ Check if the user is an admin"""

    id = event.chat.id if type(event) is Message else event.message.chat.id
    admins = Bot().get_config()["admins"]
    return id in admins


@bot.on_message(filters.command(COMMANDS) & filters.create(is_admin))
async def on_command(client: Client, message: Message):
    current_command = message.command[0]
    # await message.reply_photo(photo='AgACAgQAAxkBAAIFJ2WJTVmbFM-IGa8Bos8ZcIKES8azAAJ1vzEboU_hU-PR51fmP0veAAgBAAMCAAN4AAceBA')
    if "start" == current_command or "menu" == current_command:
        await menu(message)
    else:
        text = 'Invalid command!\nAvailable commands: \n/start\n/submit'
        await message.reply(text)
    logger.info("Conversation initiated")


@bot.on_message(filters.create(is_admin) & filters.text)
async def on_message(client: Client, message: Message):
    global user_data
    user_id = str(message.chat.id)
    if not user_data.get_user_data(user_id):
        await client.send_message(int(user_id), "To initiate our service, please run the /start command.")
    else:
        answer_user = user_data.get_user_data(user_id)
        message_id = str(message.id)
        prev_message_id = answer_user['current_message_id']

        if (answer_user and
                message_id not in answer_user):
            keyboard = await get_keyboard("submit")
            step = answer_user[prev_message_id]['step']
            text = INPUT_STATES[f"INPUT{step+1}"]
            if step == 4:
                answer_user[prev_message_id]['ad_message'] = {
                    'text': message.text}
                # TODO: force user to complete process
                # TODO: add CANCEL option
                # await client.edit_message_text(int(user_id), message_id-1, text, reply_markup=keyboard)

                await client.edit_message_text(int(user_id), int(prev_message_id), text, reply_markup=keyboard)
                # answer_users[message_id] = {}
                answer_user[prev_message_id]['step'] = 5
                # await submit_advert(client, message)
                user_data.set_user_data(user_id, answer_user)


@bot.on_message((filters.photo | filters.video | filters.media_group) & filters.caption)
async def on_message(client: Client, message: Message):
    global user_data
    user_id = str(message.chat.id)

    if not user_data.get_user_data(user_id):
        await client.send_message(int(user_id), "To initiate our service, please run the /start command.")
    else:
        answer_user = user_data.get_user_data(user_id)
        message_id = str(message.id)
        prev_message_id = answer_user['current_message_id']
        if (answer_user and
                message_id not in answer_user):

            keyboard = await get_keyboard("submit")
            step = answer_user[prev_message_id]['step']
            text = INPUT_STATES[f"INPUT{step+1}"]

            if step == 4:
                ad_message = {}
                if message.media_group_id:
                    media_group = await client.get_media_group(int(user_id), int(message_id))
                    ad_message['media_group'] = [{'type': 'photo', 'media': msg.photo.file_id, 'caption': msg.caption}if message.photo
                                                 else {'type': 'video', 'media': msg.video.file_id}
                                                 for msg
                                                 in media_group]
                elif message.photo:
                    ad_message['img'] = str(message.photo.file_id)
                elif message.video:
                    ad_message["vid"] = str(message.video.file_id)
                ad_message['text'] = message.caption

                answer_user[prev_message_id]['ad_message'] = ad_message
                # TODO: force user to complete process
                # TODO: add CANCEL option

                await client.edit_message_text(int(user_id), int(prev_message_id), text, reply_markup=keyboard)
                answer_user[prev_message_id]['step'] = 5
                user_data.set_user_data(user_id, answer_user)


@bot.on_callback_query(filters.create(is_admin))
async def on_callback_query(client: Client, callback_query: CallbackQuery):
    global user_data
    data = callback_query.data
    message = callback_query.message
    user_id = str(message.chat.id)
    message_id = str(message.id)
    answer_user = user_data.get_user_data(user_id)

    if 'step' not in answer_user[message_id]:
        answer_user[message_id]['step'] = 0
    step = answer_user[message_id]['step']

    if data == "menu" and step == 0:
        await menu(message)

    elif data == "new" and step == 0:
        await set_client_type(message)

    elif data == "confirm" and step == 5:
        await menu(message, from_confirm=True)

    elif data == "cancel" and step == 5:
        await menu(message, from_cancel=True)

    elif data == "submit":
        await submit_advert(client, message)

    elif data.startswith("select_client_"):
        choice = int(data.split("_")[-1])
        await set_duration(message, choice)

    elif data.startswith("select_duration_"):
        choice = float(data.split("_")[-2])
        await set_interval(message, choice)

    elif data.startswith("select_interval_"):
        choice = float(data.split("_")[-2])
        await accept_message(message, choice)

    await callback_query.answer()


async def menu(message: Message, from_confirm: bool = False, from_cancel: bool = False) -> None:
    """ Create the menu. """

    global user_data
    user_id = str(
        message.chat.id if from_confirm or from_cancel else message.from_user.id)
    answer_user = user_data.get_user_data(user_id)

    keyboard = await get_keyboard('menu')
    text = INPUT_STATES["INPUT0"]
    if from_confirm:
        msg = await message.edit(text, reply_markup=keyboard)
        answer_user[str(msg.id)]['step'] = 0
        schedule_message(user_id, str(message.id))
    elif from_cancel:
        msg = await message.edit(text, reply_markup=keyboard)
        answer_user[str(msg.id)]['step'] = 0
    else:
        msg = await message.reply(text, reply_markup=keyboard)
    message_id = str(msg.id)
    if message_id not in answer_user:
        answer_user[message_id] = {}
    answer_user['current_message_id'] = message_id
    answer_user[message_id]['step'] = 0
    user_data.set_user_data(user_id, answer_user)


async def set_client_type(message: Message):
    global user_data
    user_id = str(message.chat.id)
    message_id = str(message.id)
    answer_user = user_data.get_user_data(user_id)

    keyboard = await get_keyboard("client")
    step = answer_user[message_id]['step']
    text = INPUT_STATES[f"INPUT{step+1}"]
    # TODO: force user to complete process
    # TODO: add CANCEL option
    if step == 0:
        await message.edit(text, reply_markup=keyboard)
        answer_user[message_id] = {}
        answer_user[message_id]['step'] = 1
        answer_user['current_message_id'] = message_id
    user_data.set_user_data(user_id, answer_user)


async def set_duration(message: Message, client_type: float):
    global user_data
    user_id = str(message.chat.id)
    message_id = str(message.id)
    answer_user = user_data.get_user_data(user_id)

    keyboard = await get_keyboard("duration")
    step = answer_user[message_id]['step']
    text = INPUT_STATES[f"INPUT{step+1}"]
    # TODO: delete message  and add CANCEL option
    if step == 1:
        await message.edit(text, reply_markup=keyboard)
        answer_user[message_id]['step'] = 2
        answer_user[message_id]['client_type'] = client_type
        answer_user['current_message_id'] = message_id
    user_data.set_user_data(user_id, answer_user)


async def set_interval(message: Message, duration: float):
    global user_data
    user_id = str(message.chat.id)
    message_id = str(message.id)
    answer_user = user_data.get_user_data(user_id)
    keyboard = await get_keyboard("interval")
    step = answer_user[message_id]['step']
    text = INPUT_STATES[f"INPUT{step+1}"]
    # TODO: delete message  and add CANCEL option
    if step == 2:
        await message.edit(text, reply_markup=keyboard)
        answer_user[message_id]['step'] = 3
        answer_user[message_id]['duration'] = duration
        answer_user['current_message_id'] = message_id
    user_data.set_user_data(user_id, answer_user)


async def accept_message(message, interval: float):
    global answer_users
    user_id = str(message.chat.id)
    message_id = str(message.id)
    answer_user = user_data.get_user_data(user_id)

    step = answer_user[message_id]['step']
    text = INPUT_STATES[f"INPUT{step+1}"]

    if step == 3:
        await message.edit(text)
        answer_user[message_id]['step'] = 4
        answer_user[message_id]['interval'] = interval
        answer_user['current_message_id'] = message_id
    user_data.set_user_data(user_id, answer_user)


async def submit_advert(client: Client, message: Message):
    global answer_users
    user_id = str(message.chat.id)
    answer_user = user_data.get_user_data(user_id)

    prev_message_id = answer_user['current_message_id']
    data = answer_user[prev_message_id]
    advert = "Your message can not be displayed."

    advert = truncate_message(data['ad_message']['text'])
    text = "Click <b>Submit</b> to advertise your message with the following attributes:\n"
    text += f"Advert:<b> {advert}</b>\n"
    text += f"Duration:<b> {data['duration']}</b>\n"
    text += f"Interval:<b> {data['interval']}</b>\n"
    text += f"Client Type:<b> {data['client_type']}</b>\n"
    step = answer_user[prev_message_id]['step']

    keyboard = await get_keyboard('confirm')
    if step == 5:
        await client.edit_message_text(int(user_id), int(prev_message_id), text, reply_markup=keyboard)
    user_data.set_user_data(user_id, answer_user)


def schedule_message(user_id, message_id):
    global user_data
    global scheduler
    global users

    data = user_data.get_user_data(user_id)[message_id]
    logger.warning(f'Scheduling advertisement: {data}')
    duration = data['duration']
    interval = data['interval']
    ad_message = data['ad_message']
    client_type = data['client_type']  # TODO: remember to choose client types.

    now = datetime.datetime.now()
    end_date = now + datetime.timedelta(seconds=duration)
    logger.info(f'Ends on :{end_date}')
    # scheduler = AsyncIOScheduler()
    for channel_id in TARGET_CHANNELS:
        for user in users:
            random_number = randint(10, 99)
            id = f'{datetime.datetime.timestamp(now)}_{channel_id}_{user.api_id}_{random_number}'
            scheduler.add_job(
                send_message_job,
                'interval',
                seconds=interval,
                end_date=end_date,
                id=id,
                args=[bot, user, ad_message, channel_id, data, end_date])


def load_jobs_from_file(scheduler: AsyncIOScheduler, filePath: Path):
    global users
    if not os.path.exists(filePath):
        logger.error('Scheduler data file not found!')
        logger.info(f'Creating scheduler data file at {filePath}')
        with open(filePath, 'w') as file:
            json.dump({}, file, indent=4, ensure_ascii=False)
            return

    with open(filePath, 'r') as file:
        jobs_data: List = json.load(file)
        for job_data in jobs_data:
            channel_id = job_data['id'].split('_')[1]
            user_api_id = job_data['id'].split('_')[2]
            end_date = datetime.datetime.strptime(
                job_data['end_date'], '%Y-%m-%dT%H:%M:%S.%f')
            curr_user = None
            for user in users:
                if str(user.api_id) == user_api_id:
                    curr_user = user
            scheduler.add_job(
                send_message_job,
                'interval',
                seconds=job_data['data']['interval'],
                end_date=end_date,
                id=job_data['id'],
                args=[
                    bot,
                    curr_user,
                    job_data['data']['ad_message'],
                    channel_id,
                    job_data['data'],
                    end_date
                ]
            )
    logger.info(
        f"loaded {len(jobs_data)} scheduled advertisements from local storage.")


def truncate_message(message: str, length: int = 20):
    trailing = ""if len(message) < length else ". . ."
    return f'{message[:length]}{trailing}'


load_jobs_from_file(scheduler, config_dir/'scheduled_data.json')
scheduler.start()

print('============================================================================================================')


@bot.on_disconnect()
async def on_bot_exit(client: Client):
    global scheduler
    await save_jobs_to_file(scheduler, config_dir/'scheduled_data.json')

idle()

bot.stop()
for user in users:
    user.stop()
