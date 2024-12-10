from dataclasses import dataclass
from typing import Optional, Union
from discord import Member, TextChannel, Message, Interaction


@dataclass
class Game:
    """
    A class to represent a Charades game.
    
    Attributes:
    -----------
    guild_id : int
        The ID of the guild where the game is being played.
    channel : TextChannel
        The text channel where the game is taking place.
    word : str
        The word that players need to guess.
    leader : Member
        The member who is leading the game.
    game_start_time : int
        The timestamp when the game started.
    game_message : Union[Message, Interaction]
        The message or interaction associated with the game, Interaction for slash command.
    winner : Optional[Member], optional
        The member who won the game, by default None.
    """
    guild_id: int
    channel: TextChannel
    word: str
    leader: Member
    game_start_time: int
    game_end_time: int
    game_message: Union[Message, Interaction] = None

    # Game winner
    winner: Optional[Member] = None


@dataclass
class BlacklistMember:
    """
    A class used to represent a Blacklisted Member.

    Attributes
    ----------
    id : int
        The ID of the blacklisted member.
    guild_id : int
        The ID of the guild where the member is blacklisted.
    time_start : int
        The timestamp when the blacklist started.
    duration : int
        The duration of the blacklist in seconds.
    reason : Optional[str]
        The reason for the blacklist, by default None.
    """
    id: int
    guild_id: int
    time_start: int
    duration: int
    reason: Optional[str] = None
