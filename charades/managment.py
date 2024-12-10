import io
import logging
import re
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from charades.models import BlacklistMember

if TYPE_CHECKING:
    from charades.game import Charades


class CharadesManagement(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cog_charades: Charades = self.bot.get_cog('charades')
        self.word_db = self.cog_charades.words_db
        self.blacklist_db = self.cog_charades.blacklist_db

    @commands.group(
        name="charades",
        aliases=["ch"]
    )
    @commands.is_owner()
    async def charades(self, ctx: commands.Context):
        """
        Commands for manage charades game
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.charades)

    @charades.group(
        name="word_list",
        aliases=["wl", "wordlist", "wordl"]
    )
    async def word_list(self, ctx: commands.Context) -> None:
        """
        Commands for manage word list
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.word_list)

    @word_list.command(
        name="add",
        aliases=["a"],
    )
    async def word_list_add(self, ctx: commands.Context, word: str):
        """
        Add word to word list

        Parameters
        ----------
        ctx : commands.Context
        word : str
            Word to add
        """
        result = self.word_db.add_word(word)

        await ctx.send(
            f"`{word}` add to wordlist" if result else f"`{word}` already in wordlist"
        )

    @word_list.command(
        name="bulk_add",
        aliases=["ba"],
    )
    async def word_list_bulk_add(self, ctx: commands.Context):
        """
        Add words from file to word list. File must be in UTF-8 encoding and contain one word per line
        """

        if not ctx.message.attachments:
            await ctx.send("You must attach file to message with this command")
            return

        if not ctx.message.attachments[0].filename.endswith('.txt'):
            await ctx.send("File must be in .txt format")
            return

        content = await ctx.message.attachments[0].read()
        try:
            content = content.decode('utf-8')
            content = content.replace('\r', '').split('\n')
        except UnicodeDecodeError:
            await ctx.send("File must be in UTF-8")
            return

        add_length = self.word_db.bulk_add_word(content)

        await ctx.send(f"Added {add_length} words to wordlist")

    @word_list.command(
        name="remove",
        aliases=["r"],
    )
    async def word_list_remove(self, ctx: commands.Context, word: str):
        """
        Remove word from word list

        Parameters
        ----------
        ctx : commands.Context
        word : str
            Word to remove
        """
        word = word.lower().capitalize()
        result = self.word_db.remove(word)

        await ctx.send(
            f"`{word}` removed from wordlist" if result else f"`{word}` not found in wordlist",
            delete_after=5
        )

    @word_list.command(
        name="list",
        aliases=["l"],
    )
    async def word_list_list(self, ctx: commands.Context):
        """
        Generate and send file with words. All words are separated by new line. UTF-8 encoding
        """
        words = self.word_db.get_all_words()

        if not words:
            await ctx.send("Word list is empty")
            return

        words = '\n'.join(words)
        now_datetime = discord.utils.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
        file = discord.File(
            io.BytesIO(words.encode('utf-8')),
            filename=f'{now_datetime}-words.txt'
        )

        await ctx.send(file=file)

    @charades.group(
        name="black_list",
        aliases=["bl"]
    )
    async def black_list(self, ctx: commands.Context):
        """
        Commands for manage black list
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.black_list)

    @black_list.command(
        name="add",
        aliases=["a"]
    )
    async def black_list_add(
            self,
            ctx: commands.Context,
            member: discord.Member,
            duration: str,
            *,
            reason: str = "Not specified"
    ):
        """
        Add user to black list

        Parameters
        ----------
        ctx : commands.Context
        member : discord.Member
            Member to add. Can be mention or id
        duration : str
            Punishment duration. Format: 1d2h3m4s
        reason : str
            Reason for adding user to black list
        """
        if member.bot:
            await ctx.send("You can't add bot to black list")
            return

        duration = self.convert_to_seconds(duration)
        if duration == 0:
            await ctx.send("Invalid time format. Example: 1d2h3m4s")
            return

        self.blacklist_db.add_user(
            user_id=member.id,
            guild_id=ctx.guild.id,
            duration=duration,
            reason=reason
        )
        await ctx.send(f"{member.mention} added to black list for {duration} seconds")

    @black_list.command(
        name="remove",
        aliases=["r"]
    )
    async def black_list_remove(self, ctx: commands.Context, member: discord.Member):
        """
        Remove user from black list

        Parameters
        ----------
        ctx : commands.Context
        member : discord.Member
            Member to remove. Can be mention or id
        """
        result = self.blacklist_db.remove_user(
            user_id=member.id,
            guild_id=ctx.guild.id
        )

        await ctx.send(
            f"{member.mention} removed from black list" if result else f"{member.mention} not found in black list",
        )

    @black_list.command(
        name="list",
        aliases=["l"]
    )
    async def black_list_list(self, ctx: commands.Context):
        """
        Send list of black list users
        """
        black_list = self.blacklist_db.get_all_users(ctx.guild.id)
        if not black_list:
            await ctx.send("Black list is empty")
            return

        embeds = []
        for i in range(0, len(black_list), 25):
            embed = discord.Embed(
                title="Black list",
                color=discord.Color.red()
            )
            for block_usr in black_list[i:i + 25]:
                embed.add_field(
                    name=f"User ID: {block_usr.id}",
                    value=(f"**Member:** <@{block_usr.id}>\n"
                           f"**Reason:** {block_usr.reason or 'Not specified'}\n"
                           f"**Created at:** <t:{block_usr.time_start}>\n"
                           f"**Expire at:** <t:{block_usr.time_start + block_usr.duration}:R>"),
                    inline=False
                )
            embeds.append(embed)

        await ctx.send(embeds=embeds)

    @black_list.command(
        name="clear",
        aliases=["c"]
    )
    async def black_list_clear(self, ctx: commands.Context):
        """
        Clear black list
        """
        black_list = await blacklist_db.get_all_users(ctx.guild.id)
        if not black_list:
            await ctx.send("Black list is empty")
            return

        for block_usr in black_list:
            await self.blacklist_db.remove(block_usr.user_id)

        await ctx.send("Black list cleared")

    @staticmethod
    def convert_to_seconds(time_str: str) -> int:
        """
        Convert a time duration string to seconds.

        Parameters
        ----------
        time_str : str
            Time duration string in the format '1d2h3m4s', where:
            - 'd' stands for days
            - 'h' stands for hours
            - 'm' stands for minutes
            - 's' stands for seconds

        Returns
        -------
        int
            Total duration in seconds.
        """
        time_dict = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
        seconds = 0
        for time_unit, multiplier in time_dict.items():
            match = re.search(fr'(\d+){time_unit}', time_str)
            if match:
                seconds += int(match.group(1)) * multiplier
        return seconds
