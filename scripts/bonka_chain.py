import sqlite3


class BonkaApp:
    def __init__(self, user):
        self.user = user

        self.bonka_chain = sqlite3.connect('storage/bonka_chain.db')
        self.cursor = self.bonka_chain.cursor()
        print('DB Init')

    def wallet_exists(self):
        self.cursor.execute("SELECT * FROM accounts WHERE User_ID = ?", (self.user,))
        user_account = self.cursor.fetchone()[0]

        if not user_account:
            return False
        else:
            return True

    def create_wallet(self):
        self.cursor.execute("INSERT INTO accounts (User_ID, Balance) VALUES (?, 0)", (self.user,))

        self.bonka_chain.commit()
        self.bonka_chain.close()

        print(f"Created account for ID {self.user}")

    def mint_bonkas(self, recipient, amount):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (recipient,))
        user_bal = self.cursor.fetchone()[0]

        user_bal += amount

        self.cursor.execute("UPDATE accounts SET Balance = ? WHERE User_ID = ? ", (user_bal, recipient))

        self.bonka_chain.commit()
        self.bonka_chain.close()

    def destroy_bonkas(self, recipient, amount):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (recipient,))
        user_bal = self.cursor.fetchone()[0]

        if user_bal < amount:
            return False

        user_bal -= amount

        self.cursor.execute("UPDATE accounts SET Balance = ? WHERE User_ID = ? ", (user_bal, recipient))

        self.bonka_chain.commit()
        self.bonka_chain.close()

    def balance(self):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (self.user,))
        balance = self.cursor.fetchone()[0]

        self.bonka_chain.close()

        return balance

    def send_bonkas(self, recipient, amount):
        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (self.user,))
        user_bal = self.cursor.fetchone()[0]

        if user_bal < amount:
            return False

        self.cursor.execute("SELECT Balance FROM accounts WHERE User_ID = ?", (recipient,))
        recipient_bal = self.cursor.fetchone()[0]

        user_bal -= amount
        recipient_bal += amount

        self.cursor.execute("UPDATE accounts SET Balance = ? WHERE User_ID = ? ", (user_bal, self.user))
        self.cursor.execute("UPDATE accounts SET Balance = ? WHERE User_ID = ? ", (recipient_bal, recipient))

        self.bonka_chain.commit()
        self.bonka_chain.close()
