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