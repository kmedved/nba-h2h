import streamlit as st
import pandas as pd
import numpy as np

import pandas as pd
import random
import os

import pandas as pd
import s3fs

import dropbox
import csv

# Replace YOUR_API_TOKEN with your actual Dropbox API token

api_token = secrets['DROPBOX_API_TOKEN']

dbx = dropbox.Dropbox(api_token)

def read_ratings_dep():

    fs = s3fs.S3FileSystem(anon=False)

    # Retrieve file contents using pandas.
    @st.cache(ttl=600, allow_output_mutation=True)
    def read_file(filename):
        with fs.open(filename) as f:
            return pd.read_csv(f)
        
    #df = read_file("darko-streamlit/ratings.csv")

    # Get the file contents outside the `@st.cache` function.
    # This avoids the use of `S3FileSystem` inside the function.
    s3_path = "darko-streamlit/ratings.csv"
    df = read_file(s3_path)

    return df

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
#player_ratings = {player: 1500 for player in nba_df["player_name"]}
player_ratings = nba_df.set_index('player_name')['rating'].to_dict()

# Set up the initial display
player1, player2, rating1, rating2 = pick_random_players(nba_df)
st.write(f"Which player is better? {player1} or {player2}?")
choice = st.selectbox("", (player1, player2))

# Update the player ratings based on the user's choice
if choice == player1:
    result = 1
else:
    result = 0
new_rating1, new_rating2 = elo_rating(rating1, rating2, result)
player_ratings[player1] = new_rating1
player_ratings[player2] = new_rating2

# Display the updated ratings
st.write("Updated Ratings:")
nba_df["rating"] = nba_df["player_name"].apply(lambda x: player_ratings[x])
nba_df = nba_df.sort_values(by=["rating"], ascending=False)
st.write(nba_df)

# Write the DataFrame to S3 using pd.to_csv() and s3fs.

#fs = s3fs.S3FileSystem(anon=False)
#s3_path = "darko-streamlit/ratings.csv"

write_ratings(nba_df)