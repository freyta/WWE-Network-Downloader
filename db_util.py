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
            # date = timestamp
            self.c.execute("CREATE TABLE downloads (id integer unique, name text, quality text, date integer)")
            self.conn.commit()

    # Insert download into the database
    def db_ins(self, video_id, video_name, video_qual, timestamp):
        try:
            self.c.execute("INSERT INTO downloads VALUES ('{}', '{}', '{}', '{}')".format(video_id, video_name, video_qual, timestamp))
            self.conn.commit()
        except sqlite3.IntegrityError: 
            print("Error: Couldn't add {} to the database. ID already exists.".format(video_id))

    # Update download information in the database
    def db_upd(self, video_id, video_name, video_qual, timestamp):
        self.c.execute("UPDATE downloads SET name = '{}', quality = '{}', date = '{}' WHERE id = {}".format(video_name, video_qual, timestamp, video_id))
        print("UPDATE downloads SET name = '{}', quality = '{}', date = '{}' WHERE id = {}".format(video_name, video_qual, timestamp, video_id))
        self.conn.commit()

    # Query the database for previously downloaded episode
    def db_query(self, video_id):
        #self.c.execute("INSERT INTO downloads VALUES ('{}', '{}', '{}', '{}')".format(video_id, video_name, video_qual, timestamp))
        result = self.c.execute("SELECT date FROM downloads WHERE id = '{}'".format(video_id))
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