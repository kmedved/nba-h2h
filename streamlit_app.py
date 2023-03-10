import streamlit as st
import pandas as pd
import random

# Create a dictionary of basketball players with their Elo ratings
# You can replace these with your own data or use an external API
players = {
    "LeBron James": 2000,
    "Kobe Bryant": 1900,
    "Michael Jordan": 2100,
    "Magic Johnson": 1800,
    "Larry Bird": 1700,
    "Shaquille O'Neal": 1600,
    "Tim Duncan": 1700,
    "Kevin Durant": 1900,
    "Stephen Curry": 2000,
    "Kareem Abdul-Jabbar": 2200
}

# Create a DataFrame to store the Elo ratings and initialize it with the player dictionary
df = pd.DataFrame.from_dict(players, orient='index', columns=['elo'])

# Define the Elo rating calculation function
def calculate_elo_rating(winner_elo, loser_elo):
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

    # Get two random players to compare
    player1, player2 = random.sample(list(players.keys()), 2)

    # Display the players and ask the user to choose the better player
    st.write(f"**Player 1:** {player1} (Elo Rating: {df.loc[player1]['elo']})")
    st.write(f"**Player 2:** {player2} (Elo Rating: {df.loc[player2]['elo']})")

    winner, loser = st.columns(2)
    with winner:
        if st.button(f"{player1}"):
            # Update the Elo ratings based on the user's choice
            winner_elo, loser_elo = calculate_elo_rating(df.loc[player1]['elo'], df.loc[player2]['elo'])
            df.loc[player1]['elo'] = winner_elo
            df.loc[player2]['elo'] = loser_elo
            st.write(f"{player1} wins! New Elo ratings: {player1}: {winner_elo}, {player2}: {loser_elo}")

    with loser:
        if st.button(f"{player2}"):
            # Update the Elo ratings based on the user's choice
            winner_elo, loser_elo = calculate_elo_rating(df.loc[player2]['elo'], df.loc[player1]['elo'])
            df.loc[player2]['elo'] = winner_elo
            df.loc[player1]['elo'] = loser_elo
            st.write(f"{player2} wins! New Elo ratings: {player2}: {winner_elo}, {player1}: {loser_elo}")

    # Display the updated Elo ratings
    st.write(df.sort_values(by='elo', ascending=False))


if __name__ == "__main__":
    main()