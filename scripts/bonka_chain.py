import sqlite3


class BonkaApp:
    def __init__(self, user):
        self.user = user

        self.bonka_chain = sqlite3.connect('storage/bonka_chain.db')
        self.cursor = self.bonka_chain.cursor()

        table = """ CREATE TABLE IF NOT EXISTS accounts (
                User_ID INT,
                Balance INT
                );"""

        self.cursor.execute(table)

    def wallet_exists(self):
        self.cursor.execute("SELECT * FROM accounts WHERE User_ID = ?", (self.user,))
        user_account = self.cursor.fetchone()

        if user_account is not None:
            return True
        else:
            return False

    def create_wallet(self):
        self.cursor.execute("INSERT INTO accounts (User_ID, Balance) VALUES (?, 1000)", (self.user,))

        self.bonka_chain.commit()

    def mint_bonkas(self, recipient, amount):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (recipient,))
        user_bal = self.cursor.fetchone()[0]

        user_bal += amount

        self.cursor.execute("UPDATE accounts SET Balance = ? WHERE User_ID = ? ", (user_bal, recipient))

        self.bonka_chain.commit()

    def destroy_bonkas(self, recipient, amount):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (recipient,))
        user_bal = self.cursor.fetchone()[0]

        user_bal -= amount

        self.cursor.execute("UPDATE accounts SET Balance = ? WHERE User_ID = ? ", (user_bal, recipient))

        self.bonka_chain.commit()

    def balance(self):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (self.user,))
        balance = self.cursor.fetchone()[0]

        return balance

    def send_bonkas(self, recipient, amount):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (self.user,))
        user_bal = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (recipient,))
        recipient_bal = self.cursor.fetchone()[0]

        user_bal -= amount
        recipient_bal += amount

        self.cursor.execute("UPDATE accounts SET Balance = ? WHERE User_ID = ? ", (user_bal, self.user))
        self.cursor.execute("UPDATE accounts SET Balance = ? WHERE User_ID = ? ", (recipient_bal, recipient))

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