import streamlit as st
import pandas as pd
import numpy as np

import pandas as pd
import random
import os

import pandas as pd

import dropbox

def read_ratings():

    api_token = st.secrets["DROPBOX_API_TOKEN"]
    dbx = dropbox.Dropbox(api_token)

    # Define the path to the CSV file on Dropbox
    csv_file_path = '/nba_elo/ratings.csv'

    # Read CSV file from Dropbox into a pandas dataframe
    _, res = dbx.files_download(csv_file_path)
    df = pd.read_csv(res.raw)

    return df

def write_ratings(df):
    # Write the updated dataframe back to Dropbox as a CSV file

    api_token = st.secrets["DROPBOX_API_TOKEN"]
    dbx = dropbox.Dropbox(api_token)
    csv_file_path = '/nba_elo/ratings.csv'

    csv_bytes = df.to_csv(index=False).encode('utf-8')
    dbx.files_upload(csv_bytes, csv_file_path, mode=dropbox.files.WriteMode('overwrite'), mute=True)

    return


nba_df = read_ratings()

# Define the Elo rating system function
def elo_rating(rating1, rating2, result, k=32):
    expected_score1 = 1 / (1 + 10**((rating2 - rating1) / 400))
    expected_score2 = 1 - expected_score1
    new_rating1 = rating1 + k * (result - expected_score1)
    new_rating2 = rating2 + k * ((1 - result) - expected_score2)
    return new_rating1, new_rating2

# Define the function to pick two random players
def pick_random_players(nba_df):
    player1, player2 = np.random.choice(nba_df["player_name"], size=2, replace=False)
    rating1 = nba_df.loc[nba_df["player_name"] == player1, "rating"].values[0]
    rating2 = nba_df.loc[nba_df["player_name"] == player2, "rating"].values[0]
    return player1, player2, rating1, rating2

# Set up the Streamlit app
st.title("NBA Player Ratings")

# Initialize the player ratings dictionary
player_ratings = nba_df.set_index('player_name')['rating'].to_dict()

# Set up the initial display
player1, player2, rating1, rating2 = pick_random_players(nba_df)

# Define the player comparison function
st.write(f"Who is better: {player1} or {player2}?")
selected_player = st.selectbox("Select a player", [player1, player2])
if st.button("Submit"):
    if selected_player == player1:
        result = 0
        st.success(f"{player1} wins!")
    else:
        result = 1
        st.success(f"{player2} wins!")

st.write(selected_player)      

new_rating1, new_rating2 = elo_rating(rating1, rating2, result)
player_ratings[player1] = new_rating1
player_ratings[player2] = new_rating2

# Display the updated ratings
st.write("Updated Ratings:")
nba_df["rating"] = nba_df["player_name"].apply(lambda x: player_ratings[x])
nba_df = nba_df.sort_values(by=["rating"], ascending=False)
st.write(nba_df)

# Write the updated ratings to Dropbox
write_ratings(nba_df)