import pandas as pd

def load_fanduel_salaries(csv_file):
    df = pd.read_csv(csv_file)
    df = df[['Nickname', 'Position', 'Team', 'Salary']]
    return df
