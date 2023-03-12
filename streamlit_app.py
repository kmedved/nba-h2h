# import random
# import os
import dropbox
import numpy as np
import pandas as pd
import streamlit as st
from st_btn_select import st_btn_select

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
    csv_file_path = "/nba_elo/ratings.csv"

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    dbx.files_upload(
        csv_bytes, csv_file_path, mode=dropbox.files.WriteMode("overwrite"), mute=True
    )

    return

# Define the Elo rating system function
def elo_rating(rating2, rating1, result, k=32):
    expected_score1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
    expected_score2 = 1 - expected_score1
    new_rating1 = rating1 + k * (result - expected_score1)
    new_rating2 = rating2 + k * ((1 - result) - expected_score2)
    return new_rating1, new_rating2


# Define the function to pick two random players
@st.cache_data
def pick_random_players(nba_df):
    player1, player2 = np.random.choice(nba_df["player_name"], size=2, replace=False)
    rating1 = nba_df.loc[nba_df["player_name"] == player1, "rating"].values[0]
    rating2 = nba_df.loc[nba_df["player_name"] == player2, "rating"].values[0]
    return player1, player2, rating1, rating2


@st.cache_data
def read_ratings_test():
    df = pd.DataFrame(
        {
            "player_name": ["LeBron James", "Kevin Durant", "Stephen Curry"],
            "rating": [1500, 1500, 1500],
        }
    )
    return df


# Read in the ratings

nba_df = read_ratings_test()
#nba_df = _nba_df.copy(deep=True)

# Set up the Streamlit app
st.title("NBA Player Ratings")

# Initialize the player ratings dictionary
player_ratings = nba_df.set_index("player_name")["rating"].to_dict()

# # Set up the initial display
player1, player2, rating1, rating2 = pick_random_players(nba_df)


def select_player(left, right):

    with st.form(key="player_form"):
        selection = st_btn_select(
            (left, right),
            key="player_select",
        )
        submit_button = st.form_submit_button(label="Submit")
    if not submit_button:
        selection = ""

    if not submit_button:
        st.stop()
    else:
        st.write(f"***:blue[{selection}] wins!***")
        return selection


# add title:
# add a "Start Over" button
if st.button("Get new players"):
    st.cache_data.clear()
    st.experimental_rerun()

st.write("")
st.write("")

player1, player2, rating1, rating2 = pick_random_players(nba_df)
selected_player = select_player(player1, player2)
result = 1 if selected_player == player1 else 0
new_rating1, new_rating2 = elo_rating(rating1, rating2, result)
player_ratings[player1] = new_rating1
player_ratings[player2] = new_rating2

# Display the updated ratings
st.write("Updated Ratings:")
nba_df["rating"] = nba_df["player_name"].map(player_ratings)
nba_df = nba_df.sort_values(by=["rating"], ascending=False)
st.dataframe(nba_df)

# Write the updated ratings to Dropbox
# write_ratings(nba_df)

# whenever you write new data, make sure to clear your cache so you download new data on the next run:
# st.cache_data.clear()