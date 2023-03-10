import streamlit as st
import pandas as pd
import random
import os

# Create a dictionary of basketball players with their Elo ratings
# You can replace these with your own data or use an external API

# Create a DataFrame to store the Elo ratings and initialize it with the player dictionary
#df = pd.DataFrame.from_dict(players, orient='index', columns=['elo'])

# Define the Elo rating calculation function
def calculate_elo_rating(winner_elo, loser_elo):
    st.write(f"**Player 2:** {winner_elo, loser_elo})")
    k_factor = 32
    expected_win = 1 / (1 + 10**((loser_elo - winner_elo) / 400))
    actual_win = 1
    winner_elo = round(winner_elo + k_factor * (actual_win - expected_win))
    loser_elo = round(loser_elo + k_factor * (expected_win - actual_win))
    return winner_elo, loser_elo

# Define the main function for the Streamlit app
def main():
    st.title("Basketball Player Comparison App")
    st.write("Compare two random basketball players and update their Elo ratings!")

    # Load the ratings from a CSV file (if it exists)
    if os.path.isfile('ratings.csv'):
        df = pd.read_csv('ratings.csv')
    else:
        # If the file does not exist, initialize the DataFrame with the player dictionary
        print('Cannot Find file')

    # Get the player names from the DataFrame
    players = df['player_name'].tolist()

    # Get two random players to compare
    player1, player2 = random.sample(players, 2)

    player_rating_dict = df.set_index('player_name')['rating'].to_dict()

    # Display the players and ask the user to choose the better player
    st.write(f"**Player 1:** {player1} (Elo Rating: {player_rating_dict[player1]})")
    st.write(f"**Player 2:** {player2} (Elo Rating: {player_rating_dict[player2]})")

    winner, loser = st.columns(2)
    with winner:
        if st.button(f"{player1}"):
            # Update the Elo ratings based on the user's choice
            winner_elo, loser_elo = calculate_elo_rating(player_rating_dict[player1], player_rating_dict[player2])
            player_rating_dict[player1] = winner_elo
            player_rating_dict[player2] = loser_elo
            st.write(f"{player1} wins! New Elo ratings: {player1}: {winner_elo}, {player2}: {loser_elo}")

    with loser:
        if st.button(f"{player2}"):
            # Update the Elo ratings based on the user's choice
            winner_elo, loser_elo = calculate_elo_rating(player_rating_dict[player2], player_rating_dict[player1])
            player_rating_dict[player2] = winner_elo
            player_rating_dict[player1] = loser_elo
            st.write(f"{player2} wins! New Elo ratings: {player2}: {winner_elo}, {player1}: {loser_elo}")

    df = pd.DataFrame.from_dict({'player_name': list(player_rating_dict.keys()), 'rating': list(player_rating_dict.values())})

    # Display the updated Elo ratings
    st.write(df.sort_values(by='rating', ascending=False))

    # Save the updated ratings to a CSV file
    df.to_csv('ratings.csv')

if __name__ == "__main__":
    main()