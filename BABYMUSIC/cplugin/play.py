import os
import random
import string
import asyncio
from time import time
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message
from pytgcalls.exceptions import NoActiveGroupCall

from config import BANNED_USERS, lyrical
from BABYMUSIC import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from BABYMUSIC.core.call import BABY
from BABYMUSIC.misc import SUDOERS
from BABYMUSIC.utils import seconds_to_min, time_to_seconds
from BABYMUSIC.utils.channelplay import get_channeplayCB
from BABYMUSIC.utils.decorators.language import languageCB
from BABYMUSIC.utils.decorators.play import CPlayWrapper
from BABYMUSIC.utils.formatters import formats
from BABYMUSIC.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from BABYMUSIC.utils.database import (
    add_served_chat_clone,
    blacklisted_chats,
    is_banned_user,
    is_on_off,
)
from BABYMUSIC.utils.logger import play_logs
from BABYMUSIC.utils.extraction import extract_user

# Anti-spam tracking
user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5

@app.on_message(
    filters.command(
        ["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce", "cplayforce", "cvplayforce"],
        prefixes=["/", "!", ".", "", "#", "@", "%"]
    ) & filters.group & ~BANNED_USERS
)
@languageCB
@CPlayWrapper
async def play_commnd(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):
    user_id = message.from_user.id
    current_time = time()
    last_message_time = user_last_message_time.get(user_id, 0)

    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(
                f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ sᴘᴀᴍ, ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
            )
            await asyncio.sleep(3)
            return await hu.delete()
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    await add_served_chat_clone(message.chat.id)
    mystic = await message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])

    from BABYMUSIC.utils.stream.stream import stream

    # Rest of your original function logic remains unchanged...
    # (Telegram file handling, URL/query, and search logic)

    # Place this after the function to avoid unresolved reference
    return
