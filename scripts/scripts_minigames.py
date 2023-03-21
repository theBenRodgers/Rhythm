import random


def rps_game(choice):
    RPS = ('rock', 'paper', 'scissors')
    computer = random.choice(RPS)
    user = choice.lower()

    if user not in RPS:
        return "Invalid choice. Please choose 'rock', 'paper', or 'scissors'."

    outcomes = {
        ('rock', 'paper'): "I win!",
        ('rock', 'scissors'): "you win!",
        ('paper', 'rock'): "you win!",
        ('paper', 'scissors'): "I win!",
        ('scissors', 'rock'): "I win!",
        ('scissors', 'paper'): "you win!",
    }

    result = outcomes.get((user, computer), "it was a tie!")
    output = f"I picked {computer}, {result}"
    
    return output


def coin_flip():
    result = random.choice(['heads', 'tails'])
    return result
