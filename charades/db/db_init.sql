CREATE TABLE IF NOT EXISTS "blacklist" (
    "user_id"	    INTEGER NOT NULL,
    "guild_id"	    INTEGER NOT NULL,
    "created_at"	INTEGER NOT NULL,
    "duration"	    INTEGER DEFAULT 0,
    "reason"	    TEXT
);

CREATE TABLE IF NOT EXISTS "words" (
    "word"	            TEXT,
    "last_used_time"	INTEGER DEFAULT 0,
    PRIMARY KEY("word")
);

CREATE INDEX IF NOT EXISTS "idx_last_used_time" ON "words" (
    "last_used_time"
);