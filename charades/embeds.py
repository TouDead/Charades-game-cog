from typing import Optional

import discord


class EmbedTemplates:
    @staticmethod
    def base_embed(
            title: str = None,
            description: str = None
    ) -> discord.Embed:
        embed = discord.Embed(
            title=title,
            description=description,
            colour=discord.Colour.green()
        )
        embed.set_footer(text="Made by _toudead_")
        return embed

    @classmethod
    def new_game(
        cls,
        leader_user_id: int,
        time_end: int
    ) -> discord.Embed:
        embed = cls.base_embed(
            title="Game started",
            description="You have to guess the word that the leader will explain\n",
        )

        embed.add_field(name="Leader", value=f"<@{leader_user_id}>")
        embed.add_field(name="Game end at", value=f"<t:{time_end}:R>")
        
        return embed

    @classmethod
    def new_round(
        cls,
        leader_user_id: int,
        time_end: int
    ) -> discord.Embed:
        embed = cls.base_embed(
            title="New round",
            description="You have to guess the word that the leader will explain\n",
        )
        embed.add_field(name="Ведучий", value=f"<@{leader_user_id}>")
        embed.add_field(name="Гра закінчиться", value=f"<t:{time_end}:R>")
        return embed

    @classmethod
    def round_over(
            cls,
            word: str,
            winner: Optional[discord.Member] = None,
    ) -> discord.Embed:
        embed = cls.base_embed(
            title="Round over",
            description="Leader couldn't explain the word in time\n" if winner is None else None
        )
        if winner is not None:
            embed.add_field(name="Winner", value=winner.mention)
        embed.add_field(name="Word", value=word)
        return embed

    @classmethod
    def end_game(cls) -> discord.Embed:
        embed = cls.base_embed(
            title="Game ended",
            description='If you want to play again, use the command `/charades`',
        )
        return embed

    @classmethod
    def timeout_game(cls) -> discord.Embed:
        embed = cls.base_embed(
            title="Time is up",
            description="No one guessed the word in time\nIf you want to play again, use the command `/charades`",
        )
        return embed

    @classmethod
    def game_word(cls, word: str, game_channel_id: int) -> discord.Embed:
        embed = cls.base_embed(
            title=word,
            description=f"This word is a secret word for the game\n"
                        f"- You can't say this word directly\n"
                        f"- You can't use declensions or cognates\n"
                        f"- You can't use a foreign name\n"
                        f"\n"
                        f"Game channel: <#{game_channel_id}>\n",
        )
        return embed

    @classmethod
    def leader_cheating(cls, user_id: int) -> discord.Embed:
        embed = cls.base_embed(
            title="Game blocked",
            description=f"<@{user_id}> was blocked for cheating\n"
        )
        embed.colour = discord.Colour.red()
        return embed
