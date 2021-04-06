import numpy as np
import csv
import matplotlib.pyplot as plt
import itertools

style = itertools.cycle(["-","--","-.",":",".","h","H"])


def calc_expected_score(rating1, rating2):
    return 1/(1+np.power(10, ((rating2-rating1)/400)))


def calc_elo_change(rating1, rating2, score, k):
    return k*(score - calc_expected_score(rating1, rating2))


rounds = [{}]
win_record = {}

with open('elo.txt', newline='') as results:
    lines = csv.reader(results, delimiter='\t')
    for line in lines:
        if len(line) == 0:
            rounds.append({})
            for player in rounds[-2]:
                rounds[-1][player] = rounds[-2][player]
        else:
            [player_1, player_2, result] = line
            result = float(result)
            for player in [player_1, player_2]:
                if player not in rounds[-1]:
                    rounds[-2][player] = 1000
                if player not in win_record:
                    win_record[player] = {}
                    win_record[player]["Total"] = [0, 0, 0]

            if player_2 not in win_record[player_1]:
                win_record[player_1][player_2] = [0, 0, 0]  # win, lose, draw

            if player_1 not in win_record[player_2]:
                win_record[player_2][player_1] = [0, 0, 0]

            if result == 1:
                win_record[player_1][player_2][0] += 1
                win_record[player_2][player_1][1] += 1
                win_record[player_1]["Total"][0] += 1
                win_record[player_2]["Total"][1] += 1
            elif result == 0:
                win_record[player_1][player_2][1] += 1
                win_record[player_2][player_1][0] += 1
                win_record[player_1]["Total"][1] += 1
                win_record[player_2]["Total"][0] += 1
            else:
                win_record[player_1][player_2][2] += 1
                win_record[player_2][player_1][2] += 1
                win_record[player_1]["Total"][2] += 1
                win_record[player_2]["Total"][2] += 1

            k = 32
            player_1_elo = rounds[-2][player_1]
            player_2_elo = rounds[-2][player_2]
            elo_change = calc_elo_change(player_1_elo, player_2_elo, result, k)
            rounds[-1][player_1] = (player_1_elo + elo_change).round(2)
            rounds[-1][player_2] = (player_2_elo - elo_change).round(2)

players = list(rounds[-1].keys())

table_data = []
for player1 in players:
    win_percentage = []
    for player2 in players:
        if not player1 == player2:
            if player2 in win_record[player1]:
                head_to_head_record = win_record[player1][player2]
                wins = head_to_head_record[0]
                losses = head_to_head_record[1]
                draws = head_to_head_record[2]
                win_percentage.append(str(round((wins+0.5*draws)/(wins+losses+draws), 2)))
            else:
                win_percentage.append("NA")
        else:
            win_percentage.append("NA")
    total_record = win_record[player1]["Total"]
    wins = total_record[0]
    losses = total_record[1]
    draws = total_record[2]
    win_percentage.append(str(round((wins + 0.5 * draws) / (wins + losses + draws), 2)))
    table_data.append(win_percentage)

row_format ="{:>15}" * (len(players) + 2)
print(row_format.format("", *players, "Total"))
for player, row in zip(players, table_data):
    print(row_format.format(player, *row))

for player in rounds[-1]:
    elo_history = np.zeros(len(rounds))
    for i, round in enumerate(rounds):
        if player not in round:
            elo_history[i] = None
        else:
            elo_history[i] = round[player]

    plt.plot(elo_history, "-", linewidth=0.7)

plt.legend(rounds[-1], loc="best")
plt.xlabel("Round")
plt.ylabel("Elo")
plt.title("Elo History")
plt.show()

