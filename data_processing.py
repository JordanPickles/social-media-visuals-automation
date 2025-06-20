import pandas as pd
from datetime import datetime

class SponsorDataProcessor:
    def __init__(self, batting_df, bowling_df):
        self.batting_df = batting_df
        self.bowling_df = bowling_df
        self.result = None
        self.df = None

    def load_sponsor_data(self):
        CSV_URL = "https://docs.google.com/spreadsheets/d/1JaSsetNLUGFFwfDrzLu-dcT6OL2E-8Hs2yZNwlOBu5E/export?format=csv&gid=2071860895"
        try:
            self.df = pd.read_csv(CSV_URL)
        except Exception as e:
            print(e)
            exit()
        self.result = self.df[["Player Name", "Sponsor Name"]].dropna()

    def data_wrangling(self):
        self.batting_df["PlayerName"] = self.batting_df["PlayerName"].str.replace(r"[*†]", "", regex=True)
        self.bowling_df["PlayerName"] = self.bowling_df["PlayerName"].str.replace(r"[*†]", "", regex=True)
        self.batting_df["PlayerName"] = self.batting_df["PlayerName"].replace("T Stead", "Ted Stead")
        self.bowling_df["PlayerName"] = self.bowling_df["PlayerName"].replace("T Stead", "Ted Stead")

        top_6_batters = self.batting_df[
            ~self.batting_df["PlayerName"].isin(["Extras", "Total"])
        ].sort_values(["Runs", "Balls"], ascending=[False, True]).head(6)

        top_6_batters = top_6_batters.merge(
            self.result, left_on="PlayerName", right_on="Player Name", how="left"
        ).drop(columns=["Player Name"]).fillna("Available To Sponsor")

        top_6_bowlers = self.bowling_df[
            ~self.bowling_df["PlayerName"].isin(["Extras", "Total"])
        ].sort_values(["Wickets", "Runs"], ascending=[False, True]).head(6)

        top_6_bowlers = top_6_bowlers.merge(
            self.result, left_on="PlayerName", right_on="Player Name", how="left"
        ).drop(columns=["Player Name"])
        top_6_bowlers["Sponsor Name"] = top_6_bowlers["Sponsor Name"].fillna("Available to Sponsor")

        return top_6_batters, top_6_bowlers
