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
    k_factor = 32
    expected_win = 1 / (1 + 10**((loser_elo - winner_elo) / 400))
    actual_win = 1
    winner_elo = round(winner_elo + k_factor * (actual_win - expected_win))
    loser_elo = round(loser_elo + k_factor * (expected_win - actual_win))
    return winner_elo, loser_elo

def main():
    st.title("Basketball Player Comparison App")
    st.write("Compare two random basketball players and update their Elo ratings!")

    # Load the ratings from a CSV file (if it exists)
    if os.path.isfile('ratings.csv'):
        df = pd.read_csv('ratings.csv')
    else:
        st.write('Cannot find file')
        return

    # Get the player names from the DataFrame
    players = df['player_name'].tolist()

    # Create a session state to store the player ratings
    session_state = st.session_state.get(player_rating_dict={})

    # Select two random players to compare
    player1, player2 = random.sample(players, 2)

    # Get the Elo ratings of the players from the session state, or use the ratings from the DataFrame if not present
    player_rating_dict = session_state['player_rating_dict']
    if not player_rating_dict:
        player_rating_dict = df.set_index('player_name')['rating'].to_dict()
    player1_elo = player_rating_dict.get(player1, 1000)
    player2_elo = player_rating_dict.get(player2, 1000)

    # Display the players and ask the user to choose the better player
    st.write(f"**Player 1:** {player1} (Elo Rating: {player1_elo})")
    st.write(f"**Player 2:** {player2} (Elo Rating: {player2_elo})")

    # Display buttons for both players
    if st.button(f"{player1}"):
        winner_elo, loser_elo = calculate_elo_rating(player1_elo, player2_elo)
        player_rating_dict[player1] = winner_elo
        player_rating_dict[player2] = loser_elo
        session_state['player_rating_dict'] = player_rating_dict
        st.write(f"{player1} wins! New Elo ratings: {player1}: {winner_elo}, {player2}: {loser_elo}")
    st.write('')
    
    if st.button(f"{player2}"):
        winner_elo, loser_elo = calculate_elo_rating(player2_elo, player1_elo)
        player_rating_dict[player2] = winner_elo
        player_rating_dict[player1] = loser_elo
        session_state['player_rating_dict'] = player_rating_dict
        st.write(f"{player2} wins! New Elo ratings: {player2}: {winner_elo}, {player1}: {loser_elo}")

    df = pd.DataFrame.from_dict({'player_name': list(player_rating_dict.keys()), 'rating': list(player_rating_dict.values())})

    # Display the updated Elo ratings
    st.write(df.sort_values(by='rating', ascending=False))

    # Save the updated ratings to a CSV file
    df.to_csv('ratings.csv')

if __name__ == "__main__":
    main()