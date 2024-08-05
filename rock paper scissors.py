from peewee import *

choices = ['rock', 'paper', 'scissors']

db = SqliteDatabase('rps_game.db')


class BaseModel(Model):
    class Meta:
        database = db


def input_name():
    player_1_name = input("Enter player 1 name: ")
    player_2_name = input("Enter player 2 name: ")
    return player_1_name, player_2_name


def get_player_choice(player_name):
    while True:
        choice = input(f"{player_name}, Rock Paper Scissors ?: ").lower()
        if choice in choices:
            return choice
        else:
            print("Invalid input, please choose rock, paper, or scissors.")


def player_winner(player_1_choice, player_2_choice, player_1_name, player_2_name):
    if player_1_choice == player_2_choice:
        return "Draw"
    elif (player_1_choice == "rock" and player_2_choice == "scissors") or \
            (player_1_choice == "paper" and player_2_choice == "rock") or \
            (player_1_choice == "scissors" and player_2_choice == "paper"):
        return f"{player_1_name} Wins!"
    else:
        return f"{player_2_name} Wins!"


def update_score(winner, player_1_name, player_2_name, scores):
    if winner == f"{player_1_name} Wins!":
        scores[player_1_name] += 1
    elif winner == f"{player_2_name} Wins!":
        scores[player_2_name] += 1
    return scores


def player_scores(scores, player_1_name, player_2_name):
    print(f"{player_1_name} Score: {scores[player_1_name]}")
    print(f"{player_2_name} Score: {scores[player_2_name]}")


def check_game_over(scores, player_1_name, player_2_name):
    if abs(scores[player_1_name] - scores[player_2_name]) == 3:
        player_scores(scores, player_1_name, player_2_name)
        return True
    return False


def play_again():
    while True:
        replay = input("Try again? (yes or no): ").lower()
        if replay in ["yes", "y"]:
            return True
        elif replay in ["no", "n"]:
            return False
        else:
            print("Invalid input, please answer with yes or no.")


def main():
    while True:
        player_1_name, player_2_name = input_name()
        scores = {player_1_name: 0, player_2_name: 0}

        while True:
            player_1_choice = get_player_choice(player_1_name)
            player_2_choice = get_player_choice(player_2_name)

            winner = player_winner(player_1_choice, player_2_choice, player_1_name, player_2_name)
            print(winner)

            scores = update_score(winner, player_1_name, player_2_name, scores)

            if check_game_over(scores, player_1_name, player_2_name):
                break

        if not play_again():
            break


main()
