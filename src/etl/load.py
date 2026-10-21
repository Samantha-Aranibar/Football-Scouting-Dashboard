# Import needed libraries
from sqlalchemy import create_engine, text  # To create a connection to the database and execute SQL commands
import pandas as pd

# Create a connection to the database called "football_scouting.db" in the folder data/processed/
Engine = create_engine('sqlite:///../data/processed/football_scouting.db')

# Func1: Create 3 tabes in the database
def create_tables(reset = False):
    with Engine.connect() as conn:
        if reset:
            # Drop tables if they exist
            conn.execute(text("DROP TABLE IF EXISTS Match_Metrics"))
        
        # Table1: Basic player information
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS Players (
                player_id INTEGER PRIMARY KEY,
                player_name TEXT,
                position TEXT,
                nationality TEXT,
                birth_date DATE,
                height_cm DECIMAL,
                weight_kg DECIMAL,
                preferred_foot TEXT,
                market_value DECIMAL,
                current_club TEXT )
            """
        ))

        # Table2: Events from matches
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS Events (
                event_id UUID PRIMARY KEY,
                match_id INTEGER,
                player_id INTEGER REFERENCES Players(player_id),
                player_name TEXT,
                event_type TEXT,
                minute INTEGER,
                x DECIMAL,
                y DECIMAL,
                outcome TEXT,
                metadata JSONB )
            """
        ))

        # Table3: Stats calculated on each match
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS Match_Metrics (
                match_id INTEGER,
                player_id INTEGER,
                player_name TEXT,
                position TEXT,
                total_passes INTEGER,
                total_completed_passes INTEGER,       
                total_accuracy_passes DECIMAL,        
                total_progressive_passes INTEGER,
                total_long_passes INTEGER,                       
                total_won_duels INTEGER,
                total_duels INTEGER,                   
                total_successful_interceptions INTEGER,
                total_recoveries INTEGER,              
                total_tackles_won INTEGER, 
                total_shots INTEGER,
                total_goals INTEGER,
                total_assists INTEGER,
                total_xg DECIMAL,
                total_dribbles INTEGER,
                total_completed_dribbles INTEGER,           
                minutes_played INTEGER,                
                rating DECIMAL,                        
                PRIMARY KEY (match_id, player_id))
            """
            # Passes ccompleted but NO FUNC
            # Passes accuracy but NO FUNC
            # Passes long but NO FUNC 
            # Duels but NO FUNC
            # Recoveries but NO FUNC
             # Tackles won but NO FUNC
             # Minutes played but NO FUNC
             # Rating but NO FUNC
        ))

        conn.commit()

    print("Tables created successfully.")

# Func2: Save a DataFrame to a specified table in the database
def save_to_db(df: pd.DataFrame, table_name: str):
    """
    Function to save a DataFrame to a specified table in the database.
    
    Args:
        df (pd.DataFrame): The DataFrame to be saved.
        table_name (str): The name of the table where the DataFrame will be saved.
    """
    df.to_sql(table_name, Engine, if_exists='append', index = False)
    print(f"Saved: {len(df)} rows in table '{table_name}'")