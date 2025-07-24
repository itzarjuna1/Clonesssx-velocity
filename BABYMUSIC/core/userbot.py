# BABYMUSIC/userbot.py

from pyrogram import Client
import config

class Userbot(Client):
    def __init__(self):
        super().__init__(
            name="BabyUserbot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )

userbot = Userbot()