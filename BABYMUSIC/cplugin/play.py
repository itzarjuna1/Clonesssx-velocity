import os
import random
import string
import asyncio
from time import time
from pyrogram import Client, filters
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
        prefixes=["/", "!", "%", "", ".", "@", "#"]
    )
    & filters.group
    & ~BANNED_USERS
)
@userbot.on_message(  # ✅ Clone also listens to same command
    filters.command(
        ["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce", "cplayforce", "cvplayforce"],
        prefixes=["/", "!", "%", "", ".", "@", "#"]
    )
    & filters.group
    & ~BANNED_USERS
)
async def play_command(client: Client, message: Message):
    # ✅ Now both main bot & clone can handle /play
    ...
@CPlayWrapper
async def play_commnd(...):
    ...
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
                f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ sᴘᴀᴍ, ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**"
            )
            await asyncio.sleep(3)
            return await hu.delete()
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    await add_served_chat_clone(message.chat.id)
    mystic = await message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])

    # Telegram audio/video
    if message.reply_to_message:
        if message.reply_to_message.audio or message.reply_to_message.voice:
            audio = message.reply_to_message.audio or message.reply_to_message.voice
            if audio.file_size > 104857600:
                return await mystic.edit_text(_["play_5"])
            if audio.duration > config.DURATION_LIMIT:
                return await mystic.edit_text(
                    _["play_6"].format(config.DURATION_LIMIT_MIN, (await client.get_me()).mention)
                )
            file_path = await Telegram.get_filepath(audio=audio)
            if await Telegram.download(_, message, mystic, file_path):
                details = {
                    "title": await Telegram.get_filename(audio, audio=True),
                    "link": await Telegram.get_link(message),
                    "path": file_path,
                    "dur": await Telegram.get_duration(audio, file_path),
                }
                try:
                    await stream(client, _, mystic, user_id, details, chat_id, message.from_user.first_name, message.chat.id, streamtype="telegram", forceplay=fplay)
                except Exception as e:
                    return await mystic.edit_text(str(e))
                return await mystic.delete()

        elif message.reply_to_message.video or message.reply_to_message.document:
            video = message.reply_to_message.video or message.reply_to_message.document
            try:
                ext = video.file_name.split(".")[-1]
                if ext.lower() not in formats:
                    return await mystic.edit_text(_["play_7"].format(" | ".join(formats)))
            except:
                return await mystic.edit_text(_["play_7"].format(" | ".join(formats)))
            if video.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
                return await mystic.edit_text(_["play_8"])
            file_path = await Telegram.get_filepath(video=video)
            if await Telegram.download(_, message, mystic, file_path):
                details = {
                    "title": await Telegram.get_filename(video),
                    "link": await Telegram.get_link(message),
                    "path": file_path,
                    "dur": await Telegram.get_duration(video, file_path),
                }
                try:
                    await stream(client, _, mystic, user_id, details, chat_id, message.from_user.first_name, message.chat.id, video=True, streamtype="telegram", forceplay=fplay)
                except Exception as e:
                    return await mystic.edit_text(str(e))
                return await mystic.delete()

    # URL or search query
    if url:
        try:
            if await YouTube.exists(url):
                details, track_id = await YouTube.track(url)
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(details["title"], details["duration_min"])
            elif await Spotify.valid(url):
                details, track_id = await Spotify.track(url)
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_10"].format(details["title"], details["duration_min"])
            else:
                raise ValueError("Unsupported URL")
        except Exception as e:
            return await mystic.edit_text(str(e))

        if str(playmode) == "Direct":
            try:
                await stream(client, _, mystic, user_id, details, chat_id, message.from_user.first_name, message.chat.id, video=video, streamtype=streamtype, forceplay=fplay)
            except Exception as e:
                return await mystic.edit_text(str(e))
            await mystic.delete()
            return await play_logs(message, streamtype=streamtype)
        else:
            buttons = track_markup(_, track_id, user_id, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
            return await play_logs(message, streamtype=streamtype)

    if len(message.command) < 2:
        buttons = botplaylist_markup(_)
        return await mystic.edit_text(_["play_18"], reply_markup=InlineKeyboardMarkup(buttons))

    query = message.text.split(None, 1)[1]
    try:
        details, track_id = await YouTube.track(query)
        streamtype = "youtube"
    except Exception as e:
        return await mystic.edit_text(str(e))

    if str(playmode) == "Direct":
        try:
            await stream(client, _, mystic, user_id, details, chat_id, message.from_user.first_name, message.chat.id, video=video, streamtype=streamtype, forceplay=fplay)
        except Exception as e:
            return await mystic.edit_text(str(e))
        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)

    buttons = slider_markup(_, track_id, user_id, query, 0, "c" if channel else "g", "f" if fplay else "d")
    await mystic.delete()
    await message.reply_photo(photo=details["thumb"], caption=_["play_10"].format(details["title"], details["duration_min"]), reply_markup=InlineKeyboardMarkup(buttons))
    return await play_logs(message, streamtype="Youtube Search")
