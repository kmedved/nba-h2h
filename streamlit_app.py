import streamlit as st
import pandas as pd
import numpy as np
from st_btn_select import st_btn_select

import pandas as pd

# import random
# import os
import dropbox

def read_ratings():
    api_token = st.secrets["DROPBOX_API_TOKEN"]
    dbx = dropbox.Dropbox(api_token)

    # Define the path to the CSV file on Dropbox
    csv_file_path = "/nba_elo/ratings.csv"

    # Read CSV file from Dropbox into a pandas dataframe
    _, res = dbx.files_download(csv_file_path)
    df = pd.read_csv(res.raw)
    #df = pd.read_csv("local_file.csv")

    return df


def write_ratings_local(df):
    # Write the updated dataframe back to Dropbox as a CSV file

    # api_token = st.secrets["DROPBOX_API_TOKEN"]
    # dbx = dropbox.Dropbox(api_token)
    csv_file_path = "/nba_elo/ratings.csv"

    # csv_bytes = df.to_csv(index=False).encode('utf-8')
    # dbx.files_upload(csv_bytes, csv_file_path, mode=dropbox.files.WriteMode('overwrite'), mute=True)
    df.to_csv("local_write_df.csv", index=False)

    return

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
    return new_rating2, new_rating1


# Define the function to pick two random players
def pick_random_players(nba_df):
    player1, player2 = np.random.choice(nba_df["player_name"], size=2, replace=False)
    rating1 = nba_df.loc[nba_df["player_name"] == player1, "rating"].values[0]
    rating2 = nba_df.loc[nba_df["player_name"] == player2, "rating"].values[0]
    return player1, player2, rating1, rating2


def store_value(**kwargs):
    st.session_state.selected_player = st.session_state.test
    st.session_state.result = st.session_state.test
    if st.session_state.selected_player == kwargs["player1"]:
        st.session_state["result"] = f"{player1} wins!"
        result = 0
    else:
        st.session_state["result"] = f"{player2} wins!"
        result = 1

    rating1 = kwargs["rating1"]
    rating2 = kwargs["rating2"]

    new_rating1, new_rating2 = elo_rating(rating1, rating2, result)

    player_ratings = kwargs["player_ratings"]
    player_ratings[player1] = new_rating1
    player_ratings[player2] = new_rating2

    nba_df = kwargs["nba_df"]

    nba_df["rating"] = nba_df["player_name"].apply(lambda x: player_ratings[x])
    nba_df = nba_df.sort_values(by=["rating"], ascending=False)
    write_ratings(nba_df)

if __name__ == "__main__":
    # Read in the ratings
    nba_df = read_ratings()

    # Set up the Streamlit app
    st.title("NBA Player Ratings")

    # Initialize the player ratings dictionary
    player_ratings = nba_df.set_index("player_name")["rating"].to_dict()

    # Set up the initial display
    player1, player2, rating1, rating2 = pick_random_players(nba_df)

    with st.form("player_form"):
        result = st.session_state.get("result")
        if result:
            st.write(result)
            # Display the updated ratings

        player = st.radio(
            "Select best player",
            (player1, player2),
            key="test",
        )

        submitted = st.form_submit_button(
            "Submit",
            on_click=store_value,
            kwargs={
                "player1": player1,
                "player2": player2,
                "rating1": rating1,
                "rating2": rating2,
                "player_ratings": player_ratings,
                "nba_df": nba_df,
            },
        )

        if submitted:
            st.write("Updated Ratings:")
            new_values = pd.read_csv("local_write_df.csv")
            st.write(new_values)

            # Write the updated ratings to Dropbox
