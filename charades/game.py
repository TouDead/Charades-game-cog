import time
from asyncio import sleep
from typing import Dict

import discord
from discord import app_commands
from discord.ext import commands, tasks

from charades.db import WordsDatabase, BlacklistDatabase
from charades.ext import send_game_start_message, send_word_to_leader, send_game_timeout_message, \
    edit_round_over_message, send_game_end_message, send_leader_cheating_message
from charades.models import Game


@app_commands.guild_only()
class Charades(commands.GroupCog, name="charades"):
    # Duration of the game in seconds
    __GAME_DURATION = 60 * 3
    # Duration of the block leader in seconds
    __BLOCK_DURATION = 60 * 60 * 2

    def __init__(self, bot):
        self.bot = bot

        self.words_db = WordsDatabase()
        self.blacklist_db = BlacklistDatabase()
        self.games: Dict[int, Game] = {}  # channel_id: Game

        self.game_timeout_loop.start()

    async def cog_unload(self) -> None:
        self.game_timeout_loop.cancel()

    @app_commands.command(
        name="start",
        description="Start a new game. Bot will send you a word in DM, you need to explain it in the channel",
    )
    async def start(self, interaction: discord.Interaction) -> None:
        # Check if game already started
        if self.games.get(interaction.channel_id) is not None:
            await interaction.response.send_message(
                "In this channel game already started",
                ephemeral=True
            )
            return

        # Check if user is in blacklist
        if await self.is_user_in_blacklist(interaction.user.id, interaction.guild_id):
            await interaction.response.send_message(
                "You are in blacklist and can't start a game",
                ephemeral=True
            )
            return

        # Get random word
        word = self.words_db.get_random_word()
        if word is None:
            await interaction.response.send_message(
                "Word list is empty. Please contact the bot owner",
                ephemeral=True
            )
            return

        # Start game
        await self.start_game(word, interaction)

    @app_commands.command(
        name="surrender",
        description="Surrender and end game immediately. Only game leader can use this command"
    )
    async def surrender(self, interaction: discord.Interaction) -> None:
        # Check if game exists
        game = self.games.get(interaction.channel_id)
        if game is None:
            await interaction.response.send_message(
                "In this channel game not started",
                ephemeral=True
            )
            return

        # Check if user is game leader
        if interaction.user != game.leader:
            await interaction.response.send_message(
                "Only game leader can surrender",
                ephemeral=True
            )
            return

        await self.end_game(game)
        
        await interaction.response.send_message(
            "Game ended",
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        # Check if game exists
        game = self.games.get(message.channel.id)
        if game is None:
            return

        # Check if message is from game leader
        if message.author == game.leader:
            # Check if message contain game word and block leader
            if self._preprocess_word(message.content) == self._preprocess_word(game.word):
                await message.add_reaction('⛔')
                await self.block_game(game)
            return

        # Check if user is in blacklist
        if await self.is_user_in_blacklist(message.author.id, message.guild.id):
            await message.add_reaction('🚫')
            return

        # Check if message contain game word
        if self._preprocess_word(message.content) == self._preprocess_word(game.word):

            # Check if game is over
            if game.winner is not None:
                await message.add_reaction('👀')
                return

            # Set game winner
            game.winner = message.author
            await message.add_reaction('🎉')
            await self.continue_game(game, message.author)

            return

        await message.add_reaction('❌')

    # Loop for game timeout
    @tasks.loop(seconds=1)
    async def game_timeout_loop(self):
        for game in list(self.games.values()):
            if game.game_end_time < time.time():
                await self.timeout_game(game)

    @game_timeout_loop.before_loop
    async def before_game_timeout_loop(self):
        await self.bot.wait_until_ready()

    @game_timeout_loop.error
    async def game_timeout_loop_error(self, _):
        await sleep(1)
        self.game_timeout_loop.restart()
        
    async def is_user_in_blacklist(self, user_id: int, guild_id: int) -> bool:
        blacklisted = self.blacklist_db.get_user(user_id, guild_id)
        if blacklisted is not None:
            punishment_end_time = blacklisted.time_start + blacklisted.duration
            if punishment_end_time > discord.utils.utcnow().timestamp():
                return True
            else:
                self.blacklist_db.remove_user(user_id, guild_id)
        return False

    async def start_game(self, word: str, interaction: discord.Interaction):
        game = Game(
            guild_id=interaction.guild_id,
            channel=interaction.channel,
            word=word,
            leader=interaction.user,
            game_start_time=int(time.time()),
            game_end_time=int(time.time() + self.__GAME_DURATION),
            game_message=interaction
        )
        
        # send word to leader
        leader_message = await send_word_to_leader(interaction.user, word, interaction.channel.id)
        if leader_message is None:
            await interaction.response.send_message(
                "Can't send word to you. Check if you have open DM or add bot to friends",
                ephemeral=True
            )
            return
        
        # send message to game channel
        game_message = await send_game_start_message(game)
        if game_message is None:
            await leader_message.delete()
            await interaction.response.send_message(
                "Can't send message to this channel",
                ephemeral=True
            )
        
        self.games[game.channel.id] = game

    async def continue_game(self, old_game: Game, new_leader: discord.Member):
        # Get random word
        word = self.words_db.get_random_word()
        if word is None:
            await self.end_game(old_game)
            await old_game.channel.send("Word list is empty. Please contact the bot owner", delete_after=5)
            return

        # Send word to new leader
        leader_message = await send_word_to_leader(new_leader, word, old_game.channel.id)
        if leader_message is None:
            await self.end_game(old_game)
            await old_game.channel.send(
                f"Can't send word to {new_leader.display_name}. Check if you have open DM or add bot to friends",
                delete_after=5
            )
            return

        await edit_round_over_message(old_game)
        # Send message to game channel
        game_message = await send_game_start_message(old_game)
        if game_message is None:
            await self.end_game(old_game)
            await leader_message.delete()
            return

        # Create new game class
        self.games[old_game.channel.id] = Game(
            guild_id=old_game.guild_id,
            channel=old_game.channel,
            word=word,
            leader=new_leader,
            game_message=game_message,
            game_start_time=int(time.time()),
            game_end_time=int(time.time() + self.__GAME_DURATION)
        )

    async def timeout_game(self, game: Game):
        await edit_round_over_message(game)
        await send_game_timeout_message(game)
        del self.games[game.channel.id]

    async def end_game(self, game: Game):
        await edit_round_over_message(game)
        await send_game_end_message(game)
        del self.games[game.channel.id]
        
    async def block_game(self, game: Game):
        self.blacklist_db.add_user(
            user_id=game.leader.id,
            guild_id=game.guild_id,
            duration=self.__BLOCK_DURATION,
            reason="leader cheating"
        )

        await edit_round_over_message(game)
        await send_leader_cheating_message(game)
        del self.games[game.channel.id]

    @staticmethod
    def _preprocess_word(word: str) -> str:
        return (word
                .lower()
                .strip()
                .replace('`', '')
                .replace("'", "")
                .replace('"', "")
                .replace('ё', 'е')
                .capitalize()
                )
