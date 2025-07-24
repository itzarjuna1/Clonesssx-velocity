import os
import asyncio
from time import time

from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS
from BABYMUSIC import app
from BABYMUSIC.utils.decorators.language import languageCB
from BABYMUSIC.utils.decorators.play import CPlayWrapper
from BABYMUSIC.utils.database import add_served_chat_clone
from BABYMUSIC.utils.logger import play_logs

# Anti-spam trackers
user_last_message_time = {}
user_command_count = {}

SPAM_THRESHOLD = 2  # max commands
SPAM_WINDOW_SECONDS = 5  # time window

@app.on_message(
    filters.command(
        ["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce", "cplayforce", "cvplayforce"],
        prefixes=["/", "!", ".", "", "#", "@", "%"]
    ) & filters.group & ~BANNED_USERS
)
@languageCB
@CPlayWrapper
async def play_command(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):
    user_id = message.from_user.id
    current_time = time()

    # Spam protection
    last_time = user_last_message_time.get(user_id, 0)
    command_count = user_command_count.get(user_id, 0)

    if current_time - last_time < SPAM_WINDOW_SECONDS:
        user_command_count[user_id] = command_count + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            warn = await message.reply_text(
                f"**{message.from_user.mention}**, ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ sᴘᴀᴍ. ᴡᴀɪᴛ 5 sᴇᴄᴏɴᴅs."
            )
            await asyncio.sleep(3)
            return await warn.delete()
    else:
        user_command_count[user_id] = 1

    user_last_message_time[user_id] = current_time

    # Log and update database
    await add_served_chat_clone(message.chat.id)

    # Reply loading message
    loading_msg = _["play_2"].format(channel) if channel else _["play_1"]
    mystic = await message.reply_text(loading_msg)

    # Proceed to stream logic
    from BABYMUSIC.utils.stream.stream import stream
    # Add your actual stream logic here
    # Example: await stream(...)

    return