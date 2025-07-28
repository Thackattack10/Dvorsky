def project_points(row):
    return row['Goals'] * 3 + row['Assists'] * 2 + row['Shots'] * 0.5 + row['BlockedShots'] * 0.5
