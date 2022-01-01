#!/usr/bin/python3
import sqlite3
import os

class database:

    # Initialise the database
    def __init__(self):
        self.conn = sqlite3.connect("events.db")
        self.c = self.conn.cursor()


    # Connect to the database. If the file doesn't exist, it creates it.
    def db_connect(self):
        
        # Thanks to stackoverflow for help with this one.
        # https://stackoverflow.com/a/1604121
        database_exists = self.c.execute("SELECT name FROM sqlite_master WHERE name='downloads'").fetchone()
        
        if not database_exists:
            # id = DiceVideoId
            # name = the name of event/episode
            # quality = bitrate
            # partial = true/false
            # date = timestamp
            self.c.execute("CREATE TABLE downloads (id integer unique, name text, quality text, partial_download text, date integer)")
            self.conn.commit()

    # Insert download into the database
    def db_ins(self, video_id, video_name, video_qual, partial, timestamp):
        try:
            self.c.execute(f"INSERT INTO downloads VALUES ('{video_id}', '{video_name}', '{video_qual}',  '{partial}', '{timestamp}')")
            self.conn.commit()
        except sqlite3.IntegrityError: 
            print(f"Error: Couldn't add {video_id} to the database. ID already exists.")

    # Update download information in the database
    def db_upd(self, video_id, video_name, video_qual, partial, timestamp):
        self.c.execute(f"UPDATE downloads SET name = '{video_name}', quality = '{video_qual}', partial_download = '{partial}', date = '{timestamp}' WHERE id = {video_id}")
        self.conn.commit()

    # Query the database for previously downloaded episode
    def db_query(self, video_id, is_partial_download):
        if not is_partial_download:
            result = self.c.execute(f"SELECT date FROM downloads WHERE id = '{video_id}'")
        else:
            result = self.c.execute(f"SELECT date FROM downloads WHERE id = '{video_id}' AND partial_download = 'True'")
        
        if result.fetchone():
            return True
        else:
            return False

    # Close the database, and commit any final changes
    def db_close(self):
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    print("Please run python main.py instead.")
    pass