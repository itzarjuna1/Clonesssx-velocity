from pyrogram import Client
import config
from ..logging import LOGGER

assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        self.one = Client(
            name="BABYAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )

    async def start(self):
        LOGGER(__name__).info("Starting Assistants...")

        if config.STRING1:
            await self.one.start()
            try:
                await self.one.join_chat("world_friend_chatting_zone")
                await self.one.join_chat("world_friend_chatting_zone")
            except:
                pass

            # Fetch bot user details
            self.one.me = await self.one.get_me()
            self.one.id = self.one.me.id
            self.one.name = self.one.me.mention
            self.one.username = self.one.me.username

            assistants.append(1)
            assistantids.append(self.one.id)

            try:
                await self.one.send_message(config.LOGGER_ID, "✅ Assistant Started")
            except:
                LOGGER(__name__).error(
                    "❌ Assistant 1 couldn't access the log group. Make sure it's added & admin."
                )
                exit()

            LOGGER(__name__).info(f"Assistant Started as {self.one.name}")

    async def stop(self):
        LOGGER(__name__).info("Stopping Assistants...")
        try:
            if config.STRING1:
                await self.one.stop()
        except:
            pass


# Make an instance that can be imported
userbot = Userbot()