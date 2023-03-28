import mysql.connector
import json

file = open('config.json', 'r')
config = json.load(file)
database_connection = config["DATABASE"]
file.close()


class BonkaApp:
    def __init__(self, user):
        self.user = user

        self.bonka_chain = mysql.connector.connect(
            username=database_connection["username"],
            password=database_connection["password"],
            host=database_connection["host"],
            database="bonka_chain",
            port=database_connection["port"]
        )
        self.cursor = self.bonka_chain.cursor()

        table = """ CREATE TABLE IF NOT EXISTS accounts (
                User_ID BIGINT,
                Balance INT
                );"""

        self.cursor.execute(table)

    def wallet_exists(self):
        self.cursor.execute("SELECT * FROM accounts WHERE User_ID = %s", (self.user,))
        user_account = self.cursor.fetchone()

        if user_account is not None:
            return True
        else:
            return False

    def create_wallet(self):
        self.cursor.execute("INSERT INTO accounts (User_ID, Balance) VALUES (%s, 1000)", (self.user,))

        self.bonka_chain.commit()

    def mint_bonkas(self, recipient, amount):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = %s", (recipient,))
        user_bal = self.cursor.fetchone()[0]

        user_bal += amount

        self.cursor.execute("UPDATE accounts SET Balance = %s WHERE User_ID = %s ", (user_bal, recipient))

        self.bonka_chain.commit()

    def destroy_bonkas(self, recipient, amount):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = %s", (recipient,))
        user_bal = self.cursor.fetchone()[0]

        user_bal -= amount

        self.cursor.execute("UPDATE accounts SET Balance = %s WHERE User_ID = %s ", (user_bal, recipient))

        self.bonka_chain.commit()

    def balance(self):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = %s", (self.user,))
        balance = self.cursor.fetchone()[0]

        return balance

    def send_bonkas(self, recipient, amount):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = %s", (self.user,))
        user_bal = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = %s", (recipient,))
        recipient_bal = self.cursor.fetchone()[0]

        user_bal -= amount
        recipient_bal += amount

        self.cursor.execute("UPDATE accounts SET Balance = %s WHERE User_ID = %s ", (user_bal, self.user))
        self.cursor.execute("UPDATE accounts SET Balance = %s WHERE User_ID = %s ", (recipient_bal, recipient))

        self.bonka_chain.commit()

    def richest(self):
        self.cursor.execute("SELECT * FROM accounts ORDER BY Balance DESC")
        forbes = self.cursor.fetchmany(12)

        return forbes

    def economy(self):
        self.cursor.execute("SELECT Balance FROM accounts")
        economy = self.cursor.fetchall()

        return economy

    def close_app(self):
        self.bonka_chain.close()