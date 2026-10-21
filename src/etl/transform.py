# Needed libraries
import pandas as pd

# Func1: Recives all events from a match and returns only the passes
def get_passes(event: pd.DataFrame) -> pd.DataFrame:    # Recieves event as a dataframe
    """
    Function to filter and return only the pass events from a given events DataFrame.
    
    Args:
        event (pd.DataFrame): A DataFrame containing events data for a specific match.
    
    Returns:
        pd.DataFrame: A DataFrame containing only the pass events.
    """
    passes = event[event["type.name"] == "Pass"].copy()  # Filter events for passes
    passes['x'] = passes['location'].apply(lambda x: x[0] if isinstance(x, list) else None)
    passes['y'] = passes['location'].apply(lambda y: y[1] if isinstance(y, list) else None)

    return passes[["minute", "player.name", "x", "y"]]  # Return only the relevant columns

# Func2: Determines if the passes where progressive or not
def is_progressive_pass(row):
    """
    Function to determine if a pass is progressive based on its starting and ending locations.
    
    Args:
        row (pd.Series): A row from the passes DataFrame containing 'x' and 'end_location'. 
    Returns:
        bool: True if the pass is progressive and the progression, False otherwise.
    """
    # Whitout the initial location we can´t determine if the pass is progressive or not
    if not isinstance(row.get('location'), list):
        return False
    if not isinstance(row.get('pass.end_location'), list):
        return False
    start_x = row['location'][0]            # Where pass started
    end_x = row['pass.end_location'][0]     # Where pass ended  

    # Return True is a pass is progressive (moves more than 10m) and ends up in the opponent's half
    return (end_x - start_x) > 10 and end_x > 60

# Func3: Get stadistics from a specific player in a match
def build_player_match_stats(event: pd.DataFrame, player_name: str, match_id: int) -> pd.DataFrame:
    """
    Function to build player match statistics for a specific player in a given match.
    
    Args:
        event (pd.DataFrame): A DataFrame containing events data for a specific match.
        player_name (str): The name of the player for whom the statistics will be built.
        match_id (int): The ID of the match.
    Returns:
        pd.DataFrame: A DataFrame containing the player's match statistics.
    """ 
    # Filter events for the specific player
    player_events = event[event["player.name"] == player_name].copy()

    # Add a new column: "progressive_pass" to determine if the pass is progressive or not
    player_events["progressive_pass"] = player_events.apply(is_progressive_pass, axis=1)

    # Calculate the number of passes and progressive passes
    total_progressive_passes = int(player_events["progressive_pass"].sum())

    # Calculate the total number of passes
    total_passes = (player_events["type.name"] == "Pass").sum()

    # Calculate total won duels
    total_won_duels = ((player_events["type.name"] == "Duel") & (player_events["duel.outcome.name"] == "Won")).sum()

    # Total successful interceptions
    total_succesfull_interceptions = ((player_events["type.name"] == "Interception") & (player_events["interception.outcome.name"] == "Success In Play")).sum()

    # Create a summary DataFrame with the calculated statistics
    summary = pd.DataFrame([{
        "match_id": match_id,
        "player_name": player_name,
        "total_passes": total_passes,
        "total_progressive_passes": total_progressive_passes,
        "total_won_duels": total_won_duels,
        "total_succesfull_interceptions": total_succesfull_interceptions
    }])

    return summary

# Constant for Long Passes
LONG_PASS_YARDS = 32
# Func4: Create table with all players metrics and stats
def build_all_players_stats(events: pd.DataFrame, match_id: int) -> pd.DataFrame:
    """
    Build a match stats for every player in a given match.

    Args:
        events (pd.DataFrame): A DataFrame containing the events from a match.
        match_id (int): The ID of a match
    Returns:
        pd.DataFrame: One row per player with all their match statistics.
    """

    # Only events that belong to player
    df = events[events["player.name"].notna()].copy()

    # Not all matches have this columns, if they dont have it create them as empty
    for col in ["pass.outcome.name", "duel.outcome.name", "interception.outcome.name", "position.name",
                "pass.length", "pass.goal_assist", "duel.type.name", "shot.outcome.name", 
                "shot.statsbomb_xg", "dribble.outcome.name"]:
        if col not in df.columns:
            df[col] = None

    # New column (T/F) if the pass was progressive or not
    df["progressive_pass"] = df.apply(is_progressive_pass, axis = 1)

    won = ["Won", "Success In Play", "Success Out"]     # Outcomes counted as a win
    rows = []
    minutes = get_minutes_played(events)

    # One group per player
    for (player_id, player_name), g in df.groupby(["player.id", "player.name"]):
        passes = g[g["type.name"] == "Pass"]
        duels = g[g["type.name"] == "Duel"]
        interceptions = g[g["type.name"] == "Interception"]
        tackles = duels[duels["duel.type.name"] == "Tackle"]
        shots = g[(g["type.name"] == "Shot") & (g["period"] != 5)]      # period 5 = penalty shootout
        dribbles = g[g["type.name"] == "Dribble"]
        position = g["position.name"].mode()    # Most frequent positin in this match

        rows.append({
            "match_id": match_id,
            "player_id": int(player_id),
            "player_name": player_name,
            "position": position.iloc[0] if len(position) > 0 else None,
            "total_passes": len(passes),
            "total_completed_passes": int(passes["pass.outcome.name"].isna().sum()),    # Completed pass = no outcome
            "total_progressive_passes": int(passes["progressive_pass"].sum()),
            "total_won_duels": int(duels["duel.outcome.name"].isin(won).sum()),
            "total_duels": len(duels),
            "total_successful_interceptions": int(interceptions["interception.outcome.name"].isin(won).sum()),
            "total_recoveries": int((g["type.name"] == "Ball Recovery").sum()),
            "total_long_passes": int((pd.to_numeric(passes["pass.length"], errors="coerce") >= LONG_PASS_YARDS).sum()),     # HUH?
            "total_tackles_won": int(tackles["duel.outcome.name"].isin(won).sum()),
            "total_shots": len(shots),
            "total_goals": int((shots["shot.outcome.name"] == "Goal").sum()),
            "total_assists": int((passes["pass.goal_assist"] == True).sum()),
            "total_xg": round(float(pd.to_numeric(shots["shot.statsbomb_xg"], errors="coerce").sum()), 3),  # HUH?
            "total_dribbles": len(dribbles),
            "total_completed_dribbles": int((dribbles["dribble.outcome.name"] == "Complete").sum()),
            "minutes_played": minutes.get(int(player_id)),
        })

    return pd.DataFrame(rows)

# Func5: Get minutes played by each player
def get_minutes_played(events: pd.DataFrame) -> dict:
    """
    Calculate the minutes played by every player in one match.

    Args:
        events (pd.DataFrame): A DataFrame conaining the events from a match
    Returns:
        dict: {player_id: minutes_played}
    """

    # The match ends at the las minute registered (includes extra time)
    match_end = int(events["minute"].max())

    start = {}  # player_id -> minute entered
    end = {}    # player_id -> minute left

    # Starters play from minute 0
    starting_xi = events[events["type.name"] == "Starting XI"]
    for lineup in starting_xi["tactics.lineup"]:
        for p in lineup:
            player_id = int(p["player"]["id"])
            start[player_id] = 0
            end[player_id] = match_end

    # Starter players play since minute 0
    subs = events[events["type.name"] == "Substitution"]
    for _, row in subs.iterrows():
        minute = int(row["minute"])
        player_off = int(row["player.id"])
        player_on = int(row["substitution.replacement.id"])

        end[player_off] = minute
        start[player_on] = minute
        end[player_on] = match_end

    return {pid: end[pid] - start[pid] for pid in start}