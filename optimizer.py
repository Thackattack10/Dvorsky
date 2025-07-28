from pulp import LpMaximize, LpProblem, LpVariable, lpSum

def optimize_lineup(players_df):
    prob = LpProblem("FanDuel_Hockey", LpMaximize)
    var_map = {}
    for idx, row in players_df.iterrows():
        var_map[idx] = LpVariable(f"x{idx}", cat='Binary')
    # Maximize projected points
    prob += lpSum(row['Projection'] * var_map[idx] for idx, row in players_df.iterrows())
    # Salary cap constraint
    prob += lpSum(row['Salary'] * var_map[idx] for idx, row in players_df.iterrows()) <= 55000
    # Exactly 8 players
    prob += lpSum(var_map.values()) == 8
    prob.solve()
    selected = [idx for idx, v in var_map.items() if v.value() == 1]
    return players_df.loc[selected]
