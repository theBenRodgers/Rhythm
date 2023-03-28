import mysql.connector
import json

file = open('config.json', 'r')
config = json.load(file)
database_connection = config["DATABASE"]
file.close()


class MusicQueue:
    def __init__(self, guild):
        self.guild = guild

        self.queue = mysql.connector.connect(
            username=database_connection["username"],
            password=database_connection["password"],
            host=database_connection["host"],
            database="queue",
            port=database_connection["port"]
        )
        self.cursor = self.queue.cursor()

        table = """ CREATE TABLE IF NOT EXISTS queue (
        Guild BIGINT,
        Title TEXT,
        url TEXT,
        User BIGINT,
        Time_Stamp BIGINT,
        Playing TINYINT
        );"""

        self.cursor.execute(table)

    def does_queue_exist(self):
        self.cursor.execute("SELECT * FROM queue WHERE Guild = %s AND Playing = 0", (self.guild,))
        guild_queue = self.cursor.fetchone()

        if guild_queue is not None:
            return True
        else:
            return False

    def add_to_queue(self, queue_data):
        self.cursor.execute("INSERT INTO queue VALUES (%s,%s,%s,%s,%s,%s)", queue_data)

        self.queue.commit()

    def get_next_song(self):
        self.cursor.execute("SELECT * FROM queue WHERE Guild = %s AND Playing = 0", (self.guild,))
        queue_next = self.cursor.fetchone()

        return queue_next

    def get_all_songs(self):
        self.cursor.execute("SELECT * FROM queue WHERE Guild = %s AND Playing = 0", (self.guild,))
        queue_all = self.cursor.fetchall()

        return queue_all

    def clear_queue(self):
        self.cursor.execute("DELETE FROM queue WHERE Guild = %s and Playing = 0", (self.guild,))
        self.queue.commit()

    def remove_song(self, time_stamp):
        self.cursor.execute("DELETE FROM queue WHERE Guild = %s AND Time_Stamp = %s", (self.guild, time_stamp))
        self.queue.commit()

    def update_now_playing(self, time_stamp):
        self.cursor.execute("UPDATE queue SET Playing = 1 WHERE  Guild = %s AND Time_Stamp = %s", (self.guild, time_stamp))
        self.queue.commit()

    def get_now_playing(self):
        self.cursor.execute("SELECT * FROM queue WHERE Guild = %s AND Playing = 1", (self.guild,))
        playing = self.cursor.fetchone()

        return playing

    def remove_now_playing(self):
        self.cursor.execute("DELETE FROM queue WHERE  Guild = %s AND Playing = 1", (self.guild,))
        self.queue.commit()

    def close_queue(self):
        self.queue.close()
