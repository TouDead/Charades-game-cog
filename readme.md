# Charades game cog for discord.py

This is a simple cog for discord.py bot who implement charades game in text channel.
To start game use command `/charades start`, then bot will send you a private message with word to guess.
You need explain this word to other players, and they need to write in chat what they think it is.
Game will end when someone guess the word or when 3 minutes pass (duration can be changed in `game.py` file).
If user guess the word he will be new game leader and explain next word.  

If someone try to cheat and write word in chat, bot will add him to blacklist, and end game.
This user will not be able to play in this game for 2 hours (duration can be changed in `game.py` file).

Cog used own database to store words and blacklist and provide some basic commands to manage it.

# Commands

- `charades [ch]` - main group for cog
  - `wordlist [wl]` - group for wordlist management
    - `add [a]` `<word>` - add word to database
    - `bulk_add [ba]` `<attachment>` - command provide to add multiple words from file.
    You need create file with UTF-8 encoding and write to him words separated by new line.
    Each line must have only one word. Then just attach this file to message with this command when you send it.
    - `remove [r]` `<word>` - remove word from database
    - `list [l]` - send file with all words from database. Each word in new line.
  - `blacklist [bl]` - group for blacklist management
    - `add [a]` `<user> <duration> <reason>` - add user to blacklist
    - `remove [r]` `<user>` - remove user from blacklist
    - `list [l]` - display all users from blacklist for current guild
    - `clear [c]` - clear all users from blacklist for current guild


# Installation

## As a bot

Recommended to use virtual environment  
To create virtual environment go to project dir and use: `python -m venv .venv`  
To join into virtual env:
  - For *Windows* run: `.\\.venv\\Scripts\\activate` 
  - For Unix run: `./.venv/bin/activate`

To disable virtual env for current session run `deactivate` command in terminal/powershell

Next step is to install requirements `pip install -r requirements.txt`

In `bot_example.py` file set:
- your guild id in 5 line `MY_GUID = discord.Object(id=0)`
- your bot token in 26 line `bot.run('YOUR TOKEN HERE')`

To run bot use `python bot_example.py` command

## As a cog

To use this cog in your project you need to copy `charades` folder to your project directory.  
Then in your bot class add `await self.load_extension(Charades(self))` line.