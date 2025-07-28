from rapidfuzz import process

def match_names(fanduel_names, dailyfaceoff_names, score_cutoff=80):
    name_map = {}
    for short_name in fanduel_names:
        match, score, _ = process.extractOne(short_name, dailyfaceoff_names, score_cutoff=score_cutoff)
        if match:
            name_map[short_name] = match
    return name_map
