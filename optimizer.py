from pulp import LpMaximize, LpProblem, LpVariable, lpSum

def optimize_lineup(players_df):
    prob = LpProblem("FanDuel_Hockey", LpMaximize)
    var_map = {}
    for idx, row in players_df.iterrows():
        var_map[idx] = LpVariable(f"x{idx}", cat='Binary')

    # Objective: maximize projected points
    prob += lpSum(row['Projection'] * var_map[idx] for idx, row in players_df.iterrows())

    # Salary cap
    prob += lpSum(row['Salary'] * var_map[idx] for idx, row in players_df.iterrows()) <= 55000

    # Total players = 9
    prob += lpSum(var_map.values()) == 9

    # Exactly 1 goalie
    prob += lpSum(var_map[idx] for idx, row in players_df.iterrows() if row['Position'] == 'G') == 1

    # Exactly 2 centers
    prob += lpSum(var_map[idx] for idx, row in players_df.iterrows() if row['Position'] == 'C') == 2

    # Exactly 2 wingers
    prob += lpSum(var_map[idx] for idx, row in players_df.iterrows() if row['Position'] == 'W') == 2

    # Exactly 2 defensemen
    prob += lpSum(var_map[idx] for idx, row in players_df.iterrows() if row['Position'] == 'D') == 2

    # Non-goalie players = 8 (2 C + 2 W + 2 D + 2 UTIL)
    prob += lpSum(var_map[idx] for idx, row in players_df.iterrows() if row['Position'] != 'G') == 8

    prob.solve()

    selected = [idx for idx, v in var_map.items() if v.value() == 1]
    return players_df.loc[selected]
