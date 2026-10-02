# Import needed libraries
import pandas as pd
import requests 

# URL with the data
base_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

# Func1: Gets a list of competitions from the StatsBomb open data repository
def get_competitions():
    """
    Function to get competitions data from the StatsBomb open data repository.
    
    Returns:
        pd.DataFrame: A DataFrame containing competitions data.
    """
    competitions_url = f"{base_url}/competitions.json"

    ## Testtin
    competitions = pd.read_json(competitions_url)
    list_of_competitions = competitions[competitions['competition_id', 'competition_name']].copy()
    ## Done testing

    # return competitions
    return list_of_competitions.head(15)

# Func2: Get matches from a specific competition and season
def get_matches(competition_id, season_id):
    """
    Function to get matches data for a specific competition and season from the StatsBomb open data repository.
    
    Args:
        competition_id (int): The ID of the competition.
        season_id (int): The ID of the season.

    Returns:
        pd.DataFrame: A DataFrame containing matches data for the specified competition and season.
    """
    matches_url = f"{base_url}/matches/{competition_id}/{season_id}.json"
    matches = pd.read_json(matches_url)
    return matches

# Func3: Get all events from a specific match
def get_events(match_id):
    """
    Function to get all events data for a specific match from the StatsBomb open data repository.
    
    Args:
        match_id (int): The ID of the match.

    Returns:
        pd.DataFrame: A DataFrame containing events data for the specified match.
    """
    events_url = f"{base_url}/events/{match_id}.json"
    response = requests.get(events_url)
    raw = response.json()
    events = pd.json_normalize(raw)
    return events