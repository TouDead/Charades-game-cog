import discord
from discord.ext import commands
from discord import app_commands

MY_GUID = discord.Object(id=0)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def setup_hook(self) -> None:
        await self.load_extension('charades')
        self.tree.copy_global_to(guild=MY_GUID)
        await self.tree.sync(guild=MY_GUID)


bot = Bot()
bot.run('YOUR TOKEN HERE')
