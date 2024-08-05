from peewee import *

choices = ['rock', 'paper', 'scissors']

db = SqliteDatabase('rps_game.db')


class BaseModel(Model):
    class Meta:
        database = db


class Player(BaseModel):
    name = CharField(unique=True)


class GameResult(BaseModel):
    player_1 = ForeignKeyField(Player, backref='games_as_player_1')
    player_2 = ForeignKeyField(Player, backref='games_as_player_2')
    winner = CharField()
    player_1_score = IntegerField()
    player_2_score = IntegerField()
    timestamp = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


db.connect()
db.create_tables([Player, GameResult])


def input_name():
    player_1_name = input("Enter player 1 name: ")
    player_2_name = input("Enter player 2 name: ")

    player_1, created = Player.get_or_create(name=player_1_name)
    player_2, created = Player.get_or_create(name=player_2_name)

    return player_1, player_2



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
        player_1, player_2 = input_name()
        scores = {player_1.name: 0, player_2.name: 0}

        while True:
            player_1_choice = get_player_choice(player_1.name)
            player_2_choice = get_player_choice(player_2.name)

            winner = player_winner(player_1_choice, player_2_choice, player_1.name, player_2.name)
            print(winner)

            scores = update_score(winner, player_1.name, player_2.name, scores)

            if check_game_over(scores, player_1.name, player_2.name):
                GameResult.create(
                    player_1=player_1,
                    player_2=player_2,
                    winner=winner,
                    player_1_score=scores[player_1.name],
                    player_2_score=scores[player_2.name]
                )
                break

        if not play_again():
            break
    db.close()

main()
