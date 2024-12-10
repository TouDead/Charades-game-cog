import discord
from typing import Optional
from charades.embeds import EmbedTemplates
from charades.models import Game


async def send_word_to_leader(leader: discord.Member, word: str, game_channel_id: int) -> Optional[discord.Message]:
    try:
        message = await leader.send(embed=EmbedTemplates.game_word(word, game_channel_id))
        return message
    except discord.Forbidden:
        return None


async def send_game_start_message(game: Game) -> Optional[discord.Message]:
    try:
        if isinstance(game.game_message, discord.Interaction):
            await game.game_message.response.send_message(
                embed=EmbedTemplates.new_game(game.leader.id, game.game_end_time)
            )
            return game.game_message
        else:
            message = await game.channel.send(embed=EmbedTemplates.new_game(game.leader.id, game.game_end_time))
            return message
    except discord.Forbidden:
        return None


async def send_game_timeout_message(game: Game) -> Optional[discord.Message]:
    try:
        message = await game.channel.send(embed=EmbedTemplates.timeout_game())
        return message
    except discord.Forbidden:
        return None


async def send_game_end_message(game: Game) -> Optional[discord.Message]:
    try:
        message = await game.channel.send(embed=EmbedTemplates.end_game())
        return message
    except discord.Forbidden:
        return None


async def send_leader_cheating_message(game: Game) -> Optional[discord.Message]:
    try:
        message = await game.channel.send(embed=EmbedTemplates.leader_cheating(game.leader.id))
        return message
    except discord.Forbidden:
        return None


async def edit_round_over_message(game: Game) -> discord.Message:
    embed = EmbedTemplates.round_over(game.word, game.winner)
    if isinstance(game.game_message, discord.Interaction):
        await game.game_message.edit_original_response(embed=embed)
    else:
        await game.game_message.edit(embed=embed)
    return game.game_message
