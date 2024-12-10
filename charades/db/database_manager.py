import os
import sqlite3
from time import time
from typing import List, Optional
from charades.models import BlacklistMember


def preprocess_word(word: str) -> str:
    """
    Transform the word to a format suitable for storing in the database.
    """
    word = word.split()[0]
    return word.strip().lower().capitalize()


class WordsDatabase:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "charades.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.__create_if_not_exists(os.path.join(base_dir, "db_init.sql"))

    def __create_if_not_exists(self, init_file_path: str):
        with open(init_file_path, "r") as file:
            self.cursor.executescript(file.read())
            self.conn.commit()

    def add_word(self, word) -> bool:
        """
        Adds a word to the database if it does not already exist.

        Parameters
        ----------
        word : str
            The word to be added to the database.

        Returns
        -------
        bool
            True if the word was successfully added, False if the word already exists.
        """
        insert_query = "INSERT OR IGNORE INTO words (word) VALUES (?)"
        self.cursor.execute(insert_query, (preprocess_word(word),))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def bulk_add_word(self, word_list: List[str]) -> int:
        """
        Adds a list of words to the database in bulk, ignoring duplicates.

        Parameters
        ----------
        word_list : List[str]
            A list of words to be added to the database.

        Returns
        -------
        int
            The number of words successfully added to the database.
        """
        preprocessed_words = [(preprocess_word(word),) for word in word_list if word]
        insert_query = "INSERT OR IGNORE INTO words (word) VALUES (?)"
        with self.conn:
            self.cursor.executemany(insert_query, preprocessed_words)

        return self.cursor.rowcount

    def remove_word(self, word) -> bool:
        """
        Remove a word from the database.

        Parameters
        ----------
        word : str
            The word to be removed from the database.

        Returns
        -------
        bool
            True if the word was successfully removed, False otherwise.
        """
        delete_query = "DELETE FROM words WHERE word = ?"
        self.cursor.execute(delete_query, (preprocess_word(word),))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_random_word(self, limit=5) -> Optional[str]:
        """
        Retrieve a random word with the least used time from the database.
        
        Parameters
        ----------
        limit : int, optional
            The number of random words to fetch from the database (default is 5).
            
        Returns
        -------
        Optional[str]
            A single random word from the database or None if the database is empty.
        """
        select_query = "SELECT word, last_used_time FROM words ORDER BY RANDOM() LIMIT ?"
        self.cursor.execute(select_query, (limit,))
        words = self.cursor.fetchall()

        if not words:
            return None

        word = min(words, key=lambda x: x[1])[0]

        update_query = "UPDATE words SET last_used_time = ? WHERE word = ?"
        self.cursor.execute(update_query, (str(int(time())), word))
        self.conn.commit()

        return word

    def get_all_words(self) -> List[str]:
        """
        Retrieve all words from the database.

        Returns
        -------
        List[str]
            A list of words retrieved from the database.
        """
        select_query = "SELECT word FROM words"
        self.cursor.execute(select_query)
        words = self.cursor.fetchall()
        return [word[0] for word in words]


class BlacklistDatabase:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "charades.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def add_user(self, user_id: int, guild_id: int, duration: int, reason: Optional[str] = None) -> bool:
        """
        Add a user to the blacklist in the database.

        Parameters
        ----------
        user_id : int
            The ID of the user to be blacklisted.
        guild_id : int
            The ID of the guild where the user is blacklisted.
        duration : int
            The duration of the blacklist in seconds.
        reason : Optional[str], optional
            The reason for the blacklist, by default None.

        Returns
        -------
        bool
            True if the user was successfully blacklisted, False otherwise.
        """
        insert_query = "INSERT INTO blacklist (user_id, guild_id, created_at, duration, reason) VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(insert_query, (user_id, guild_id, int(time()), duration, reason))
        self.conn.commit()
        return self.cursor.rowcount > 0
  
    def remove_user(self, user_id: int, guild_id: int) -> bool:
        """
        Remove a user from the blacklist in the database.

        Parameters
        ----------
        user_id : int
            The ID of the user to be removed from the blacklist.
        guild_id : int
            The ID of the guild where the user is blacklisted.

        Returns
        -------
        bool
            True if the user was successfully removed from the blacklist, False otherwise.
        """
        delete_query = "DELETE FROM blacklist WHERE user_id = ? AND guild_id = ?"
        self.cursor.execute(delete_query, (user_id, guild_id))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_user(self, user_id: int, guild_id: int) -> Optional[BlacklistMember]:
        """
        Retrieve a blacklisted user from the blacklist in the database.

        Parameters
        ----------
        user_id : int
            The ID of the user to retrieve from the blacklist.
        guild_id : int
            The ID of the guild where the user is blacklisted.

        Returns
        -------
        Optional[BlacklistMember]
            A BlacklistMember object representing the blacklisted user or None if the user is not blacklisted.
        """
        select_query = "SELECT * FROM blacklist WHERE user_id = ? AND guild_id = ?"
        self.cursor.execute(select_query, (user_id, guild_id))
        user = self.cursor.fetchone()
        return BlacklistMember(*user) if user else None
    
    def get_all_users(self, guild_id: int) -> List[BlacklistMember]:
        """
        Retrieve all blacklisted users from the blacklist in the database.

        Returns
        -------
        List[BlacklistMember]
            A list of BlacklistMember objects representing the blacklisted users.
        """
        select_query = "SELECT * FROM blacklist WHERE guild_id = ?"
        self.cursor.execute(select_query, (guild_id,))
        users = self.cursor.fetchall()
        return [BlacklistMember(*user) for user in users]
