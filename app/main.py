import hashlib
import datetime
from pathlib import Path
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pyrogram import Client, filters, idle
from pyrogram.types import (Message, CallbackQuery )

from forward import users
from config import Forwarding, Bot
from modules import get_keyboard, create_keyboard, UserStateManager

from logger import logger


# Config path
app_dir = Path(__file__).parent
config_dir = app_dir / "config"
TARGET_CHANNELS = [-1002123309124,-1002039852753]

# Load the bot configuration
bot_config = Bot().get_config()[0]
forwardings = Forwarding()
bots: List[Client] = []
API_ID = bot_config["api_id"]
API_HASH = bot_config["api_hash"]
bot = Client(
    str(Path(config_dir/f"bot{API_ID}")),
    api_id=API_ID,
    api_hash=API_HASH,
    # bot_token=''
)
bots.append(bot)
logger.info(f"BOT @{API_ID} configured")
scheduler = AsyncIOScheduler()
commands = ["start", "menu"]
INPUT_STATES = {
    "INPUT0": "Launch a Rocket Advert",
    "INPUT1": "Which channel type to send the message to?",
    "INPUT2": "For how long do you want to advertise?",
    "INPUT3": "How often do you want to advertise your message?",
    "INPUT4": "Send the advertisement message in the text area below...",
    "INPUT5": "To start sending the message, click the submit button"
}
commands = ["start", "menu", "submit"]
answer_users = {}
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

# Lambda function to create a hash from a string
async def md5(word): return hashlib.md5(word.encode("utf-8")).hexdigest()


async def is_admin(filter, client: Client, event: Message | CallbackQuery):
    """ Check if the user is an admin"""

    id = event.chat.id if type(event) is Message else event.message.chat.id
    admins = Bot().get_config()[0]["admins"]
    return id in admins

@bot.on_message(filters.command(commands) & filters.create(is_admin)  )
async def on_command(client: Client, message: Message):
    current_command = message.command[0]
    if "start" == current_command or "menu" == current_command:
        await menu(message)
    logger.info("Conversation initiated")

@bot.on_message(filters.create(is_admin))
async def on_message(client: Client, message: Message):
    global answer_users
    user_id = message.chat.id
    message_id = message.id
    prev_message_id = answer_users[user_id]['current_message_id']
    
    if user_id not in answer_users:
        await client.send_message(user_id, "To initiate our service, please run the /start command.")
    
    if (answer_users and
        user_id in answer_users and
        message_id not in answer_users[user_id]):
        keyboard = await get_keyboard("submit")
        step = answer_users[user_id][prev_message_id]['step']
        text = INPUT_STATES[f"INPUT{step+1}"]
        if step == 4:
            answer_users[user_id][prev_message_id]['ad_message']=message
            # TODO: force user to complete process
            # TODO: add CANCEL option
            # await client.edit_message_text(user_id, message_id-1, text, reply_markup=keyboard)
            
            await client.edit_message_text(user_id, prev_message_id, text, reply_markup=keyboard)
            # answer_users[user_id][message_id] = {}
            answer_users[user_id][prev_message_id]['step'] = 5
            # await submit_advert(client, message)
            

@bot.on_callback_query(filters.create(is_admin))
async def on_callback_query(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    message = callback_query.message
    user_id = message.chat.id
    message_id = message.id
    # answer_users[user_id] = [False, None, None]
    if 'step' not  in answer_users[user_id][message_id]:
        answer_users[user_id][message_id]['step'] = 0
    step = answer_users[user_id][message_id]['step']
    
    if data == "menu" and (step == 0 or step == 5):
        await menu(message)
    elif data == "new":
        await set_client_type(message)
    elif data == "confirm" and step == 5:
        await menu(message,from_confirm = True)
    elif data == "submit":
        await submit_advert(client, message)
    
    # elif data == "cancel" and step == 5:
    #     await menu(message)
    
    elif data.startswith("select_client_"):
        choice = int(data.split("_")[-1])
        await set_duration(message, choice)

    elif data.startswith("select_duration_"):
        choice = float(data.split("_")[-2])
        await set_interval(message, choice)

    elif data.startswith("select_interval_"):
        choice = float(data.split("_")[-2])
        await accept_message(message,choice)
    
    await callback_query.answer()

async def menu(message: Message, from_confirm: bool = False) -> None:
    """ Create the menu. """
    
    global answer_users
    user_id = message.chat.id if from_confirm else message.from_user.id
    
    keyboard = await get_keyboard('menu')
    text = INPUT_STATES["INPUT0"]
    if from_confirm:
        msg = await message.edit(text, reply_markup=keyboard)
        answer_users[user_id][msg.id]['step']=0
        await schedule_message(user_id, message.id)
    else:
        msg = await message.reply(text, reply_markup=keyboard)
    if user_id not in answer_users:
        answer_users[user_id] = {}
    if msg.id not in answer_users[user_id]:
        answer_users[user_id][msg.id] = {}
    answer_users[user_id]['current_message_id'] = msg.id
    answer_users[user_id][msg.id]['step']=0

async def set_client_type(message: Message):
    global answer_users
    user_id = message.chat.id
    message_id = message.id

    keyboard = await get_keyboard("client")
    step = answer_users[user_id][message_id]['step']
    text = INPUT_STATES[f"INPUT{step+1}"]
    # TODO: force user to complete process
    # TODO: add CANCEL option
    if  step == 0:
        await message.edit(text, reply_markup=keyboard)
        answer_users[user_id][message_id] = {}
        answer_users[user_id][message_id]['step'] = 1
        answer_users[user_id]['current_message_id'] = message_id

    else:
        logger.warning("Step incorrect")

async def set_duration(message: Message, client_type: float):
    global answer_users
    user_id = message.chat.id
    message_id = message.id
    keyboard = await get_keyboard("duration")
    step = answer_users[user_id][message_id]['step']
    text = INPUT_STATES[f"INPUT{step+1}"]
    # TODO: delete message  and add CANCEL option
    if step == 1:
        await message.edit(text, reply_markup=keyboard)
        answer_users[user_id][message_id]['step'] = 2
        answer_users[user_id][message_id]['client_type'] = client_type
        answer_users[user_id]['current_message_id'] = message_id
    else:
        logger.info("Step incorrect")

async def set_interval(message: Message, duration: float):
    global answer_users
    user_id = message.chat.id
    message_id = message.id
    keyboard = await get_keyboard("interval")
    step = answer_users[user_id][message_id]['step']
    text = INPUT_STATES[f"INPUT{step+1}"]
    # TODO: delete message  and add CANCEL option
    if step == 2:
        await message.edit(text, reply_markup=keyboard)
        answer_users[user_id][message_id]['step'] = 3
        answer_users[user_id][message_id]['duration'] = duration
        answer_users[user_id]['current_message_id'] = message_id

    else:
        logger.info("Step incorrect")
    
async def accept_message(message, interval: float):
    global answer_users
    user_id = message.chat.id
    message_id = message.id
    step = answer_users[user_id][message_id]['step']
    text = INPUT_STATES[f"INPUT{step+1}"]

    if step ==3:
        await message.edit(text)
        answer_users[user_id][message_id]['step'] = 4
        answer_users[user_id][message_id]['interval'] = interval
        answer_users[user_id]['current_message_id'] = message_id
    else:
        logger.warning("Step incorrect")
    
async def submit_advert(client:Client, message:Message):
    global answer_users
    user_id = message.chat.id
    prev_message_id = answer_users[user_id]['current_message_id']
    data = answer_users[user_id][prev_message_id]
    text = "Click submit to advertise your message with the following attributes:\n"
    text+= f"message: {truncate_message(data['ad_message'].text)}\n"
    text += f"Duration: {data['duration']}\n"
    text += f"Interval: {data['interval']}\n"
    text += f"Client Type: {data['client_type']}\n"
    step = answer_users[user_id][prev_message_id]['step']

    keyboard = await get_keyboard('confirm')
    if step == 5:
        await client.edit_message_text(user_id, prev_message_id,text,reply_markup=keyboard)
    # answer_users[user_id]['current_message_id'] = message_id
  
async def schedule_message(user_id, message_id):
    global answer_users
    global scheduler
    global users
    data = answer_users[user_id][message_id]
    print(data)
    duration = data['duration']
    interval = data['interval']
    ad_message = data['ad_message']
    client_type = data['client_type'] #TODO: remember to choose client types.
    
    now= datetime.datetime.now()
    end_date= now + datetime.timedelta(seconds= duration)
    # scheduler = AsyncIOScheduler()
    for channel_id in TARGET_CHANNELS:
        for user in users:
            id = f'{datetime.datetime.timestamp(now)}_{channel_id}_{user.api_id}'
            scheduler.add_job(
                send_message_job,
                'interval', 
                seconds=interval,
                end_date=end_date,
                id=id,
                args=[user, ad_message, channel_id] )
  
async def send_message_job(client:Client, message, channel_id):
    logger.debug(f'✔️ FROM{client.api_id} to {channel_id}')
    await client.send_message(channel_id, message.text)
    
def truncate_message(message:str, length:int=20):
    trailing = ""if len(message) < length else". . ."
    return f'{message[:length]}{trailing}'

if not Path(config_dir/f"bot{bot.api_id}.session").exists():
    logger.info("Log-in with you bot token")
bot.start()
logger.info("Bot started")
logger.info(f"Bot username: @{bot.get_me().username}")
scheduler.start()
idle()
bot.stop()

for user in users:
    user.stop()