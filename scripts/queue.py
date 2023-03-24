import sqlite3

class Queue:
    def __init__(self, guild):
        self.guild = guild

        self.queue = sqlite3.connect('storage/queue.db')
        self.cursor = self.queue.cursor()

        table = """ CREATE TABLE IF NOT EXISTS queue (
        Guild INT,
        Title TEXT,
        url TEXT,
        User INT,
        Time_Stamp INT,
        Playing INT
        );"""

        self.cursor.execute(table)

    def queue_exists(self):
        self.cursor.execute("SELECT * FROM queue WHERE Guild = ? AND Playing = 0", (self.guild,))
        guild_queue = self.cursor.fetchone()

        if guild_queue is not None:
            return True
        else:
            return False

    def queue_add(self, queue_data):
        self.cursor.execute("INSERT INTO queue VALUES (?,?,?,?,?,?)", queue_data)

        self.queue.commit()

    def queue_next(self):
        self.cursor.execute("SELECT * FROM queue WHERE Guild = ? AND Playing = 0 ORDER BY Time_Stamp ASC", (self.guild,))
        queue_next = self.cursor.fetchone()

        return queue_next

    def queue_all(self):
        self.cursor.execute("SELECT * FROM queue WHERE Guild = ? AND Playing = 0 ORDER BY Time_Stamp ASC", (self.guild,))
        queue_all = self.cursor.fetchall()

        return queue_all

    def queue_clear(self):
        self.cursor.execute("DELETE FROM queue WHERE Guild = ?", (self.guild,))
        self.queue.commit()

    def queue_remove(self, time_stamp):
        self.cursor.execute("DELETE FROM queue WHERE Guild = ? AND Time_Stamp = ?", (self.guild, time_stamp))
        self.queue.commit()

    def set_now_playing(self, time_stamp):
        self.cursor.execute("SELECT * FROM queue WHERE  Guild = ? AND Playing = 1", (self.guild, time_stamp))
        self.queue.commit()

    def now_playing(self):
        self.cursor.execute("SELECT * FROM queue WHERE Guild = ? AND Playing = 1", (self.guild,))
        playing = self.cursor.fetchone()

        return playing

    def set_not_playing(self, time_stamp):
        self.cursor.execute("SELECT * FROM queue WHERE  Guild = ? AND Playing = 0", (self.guild, time_stamp))
        self.queue.commit()

    def queue_close(self):
        self.queue.close()