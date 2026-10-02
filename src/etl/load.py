# Import needed libraries
from sqlalchemy import create_engine
import pandas as pd

# Create a connection to the database called "football_scouting.db" in the folder data/processed/
Engine = create_engine('sqlite:///../data/processed/football_scouting.db')

# Func1: Load a DataFrame into a specified table in the database
def save_to_db(df: pd.DataFrame, table_name: str):
    """
    Function to save a DataFrame to a specified table in the database.
    
    Args:
        df (pd.DataFrame): The DataFrame to be saved.
        table_name (str): The name of the table in the database where the DataFrame will be saved.
    """
    # to_sql() method to save the DataFrame to the specified table in the database
    # if_exists='replace' will replace the table if it already exists
    df.to_sql(table_name, Engine, if_exists='replace', index=False)

    print(f"Saved: {len(df)} rows to table named {table_name}.")
