import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

from config import BANNED_USERS, STRING1
from BABYMUSIC import LOGGER, app, userbot
from BABYMUSIC.core.call import BABY
from BABYMUSIC.misc import sudo
from BABYMUSIC.plugins import ALL_MODULES
from BABYMUSIC.utils.database import get_banned_users, get_gbanned
from BABYMUSIC.plugins.tools.clone import restart_bots


async def init():
    if not STRING1:
        LOGGER(__name__).error("⚠️ STRING1 is missing! Fill it in config.py or .env.")
        return

    await sudo()

    # Load global bans
    try:
        gbanned = await get_gbanned()
        for user_id in gbanned:
            BANNED_USERS.add(user_id)

        banned = await get_banned_users()
        for user_id in banned:
            BANNED_USERS.add(user_id)

    except Exception as e:
        LOGGER("BABYMUSIC").warning(f"Failed to fetch banned users: {e}")

    # Start clients
    await app.start()
    await userbot.start()

    # Import all plugins
    for module in ALL_MODULES:
        importlib.import_module(f"BABYMUSIC.plugins.{module}")
    LOGGER("BABYMUSIC.plugins").info("✅ All Plugin Modules Loaded Successfully!")

    # Start PyTgCalls
    await BABY.start()
    try:
        await BABY.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("BABYMUSIC").error(
            "❌ Start a voice chat in the log group/channel to enable streaming!"
        )
        return
    except Exception as e:
        LOGGER("BABYMUSIC").warning(f"Stream call failed: {e}")

    await BABY.decorators()
    await restart_bots()

    LOGGER("BABYMUSIC").info("🤖 Infinity AI Music Bot Started Successfully!")
    await idle()

    # Shutdown
    await app.stop()
    await userbot.stop()
    LOGGER("BABYMUSIC").info("🛑 Bot Stopped Cleanly.")


if __name__ == "__main__":
    asyncio.run(init())