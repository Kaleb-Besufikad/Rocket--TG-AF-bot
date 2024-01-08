
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatType, MessageMediaType
from pyrogram.types import (Message, CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup)
from pyrogram.errors.exceptions.bad_request_400 import (ChannelInvalid,
                                                        PeerIdInvalid,
                                                        UsernameNotOccupied,
                                                        UsernameInvalid)
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

client_keyboard = [
    [{"📱 Client type 1": "select_client_0"},
    {"⚒️ Test Clients": "select_client_1"}
    ],
    #[{"💊 Client type 3": "select_client_2"},
    #{"👔 Client type 4": "select_client_3"}]
]

# ONLY IN DAYS
duration_keyboard = [
    [{'1 Day': 'select_duration_1_days' }],
    [{'15 Days': 'select_duration_15_days'},
    {'1 Month': 'select_duration_30_days'}],
    
]

# ONLY IN HOURS
interval_keyboard = [
    [{'Every 2 Minutes': 'select_interval_0.0333_hours'},
    {'Every 15 Minutes': 'select_interval_0.25_hours'}],
    [{'Every 30 Hour': 'select_interval_0.5_hours'},
    {'Every 1 Hour': 'select_interval_1_hours'}],
    [{'Every 2 Hours': 'select_interval_2_hours'}],
]

menu_keyboard = [
        [{"➕ Create Advertisement": "new"}],
    # [{"🔥 See Ads": "ads"}], #TODO: show all advertisements to admins
    ]

submit_keyboard = [
    [{'📩 Submit': 'submit'}, {'❌ Cancel': 'cancel'}]
]
confirm_keyboard = [
        [{'✅ Confirm': 'confirm'}, {'❌ Cancel': 'cancel'}]
]


async def create_keyboard(buttons: list) -> InlineKeyboardMarkup:
    """ Create a keyboard with the given buttons.

    Parameters
    ----------
    buttons : list
        A list with the buttons to create.
        The keys are the button text and the values are the callback data.

    Returns
    -------
    InlineKeyboardMarkup
        The keyboard with the given buttons.
    """
    keyboard = []
    # Create the buttons
    for i, button_index in enumerate(buttons):
        keyboard.append([])
        for button in button_index:
            for key, value in button.items():
                keyboard[i].append(InlineKeyboardButton(key, value))

    return InlineKeyboardMarkup(keyboard)


async def get_keyboard(kb_type: str):

    match kb_type:
        case "client":
            return await create_keyboard(client_keyboard)
        case "duration":
            return await create_keyboard(duration_keyboard)
        case "interval":
            return await create_keyboard(interval_keyboard)
        case 'menu':
            return await create_keyboard(menu_keyboard)
        case 'submit':
            return await create_keyboard(submit_keyboard)
        case 'confirm':
            return await create_keyboard(confirm_keyboard)
        case _:
            return InlineKeyboardMarkup([])
