import requests
from bs4 import BeautifulSoup
import pandas as pd
class ScorecardAPICall:
    """
    ScorecardAPICall provides methods to fetch and process cricket match scorecard data from two different APIs:
    the NVPlay API and the Results Vault API. It supports retrieving match data, extracting batting and bowling
    statistics, and returning the results as pandas DataFrames.
    Attributes:
        match_number (str or int): The unique identifier for the cricket match.
        team_name (str): The name of the team for which data is to be fetched.
        api_header (str): API header value required for Results Vault API authentication.
        customer_id (str): Customer ID for NVPlay API requests.
        nv_url (str): URL template for NVPlay API scorecard endpoint.
        results_vault_match_id_url (str): URL template to fetch Results Vault match ID mapping.
        headers (dict): Default HTTP headers for API requests.
    Methods:
        nv_api_call():
            Fetches scorecard data from the NVPlay API for the specified match.
        _get_match_id_results_vault():
            Retrieves the Results Vault match ID corresponding to the given match number.
        results_vault_api_call():
            Fetches detailed match data from the Results Vault API using the mapped match ID.
        nv_process_data(data):
            Processes NVPlay API response data to extract batting and bowling statistics.
            Returns:
                Tuple[pd.DataFrame, pd.DataFrame]: Batting and bowling data as DataFrames.
        results_vault_process_data(data):
            Processes Results Vault API response data to extract batting and bowling statistics.
            Returns:
                Tuple[pd.DataFrame, pd.DataFrame]: Batting and bowling data as DataFrames.
        get_scorecard():
            Attempts to fetch scorecard data from NVPlay API, falling back to Results Vault API if necessary.
            Returns:
                dict: Raw scorecard data.
        process_data(data):
            Determines the source of the data and processes it accordingly to extract statistics.
            Returns:
                Tuple[pd.DataFrame, pd.DataFrame]: Batting and bowling data as DataFrames.
    """

    def __init__(self, match_number, team_name, api_header):
        self.match_number = match_number
        self.team_name = team_name
        self.customer_id = "5e401d65-10ec-4a28-a0f6-1c084ce30445"
        self.nv_url = f"https://w-api2.ecb.nvplay.net/api/scorecard/{match_number}"
        self.results_vault_match_id_url =  f"https://api-alb.resultsvault.co.uk/rv/mappings/4/12/{match_number}/?apiid=1002&sportid=1"
        self.api_header = api_header
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

    def nv_api_call(self):
        """
        Makes an API call to the NV endpoint to retrieve player information, statistics, and commentary.
        Sends a GET request with specific parameters including player IDs, statistics, and commentary flags.
        Raises an HTTPError if the request fails.
        Returns:
            dict: The JSON response from the NV API containing player data, statistics, and commentary.
        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """

        params = {
            "idType": "play-cricket",
            "customerId": self.customer_id,
            "playerids": "true",
            "stats": "true",
            "commentary": "true"
        }
        response = requests.get(self.nv_url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def _get_match_id_results_vault(self):
        """
        Fetches the match ID from the Results Vault API endpoint.
        Sends a GET request to the Results Vault match ID URL using custom headers,
        parses the JSON response, and retrieves the value associated with the "object_id1" key.
        Returns:
            str or None: The match ID retrieved from the Results Vault, or None if not found.
        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """

        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "x-ias-api-request": self.api_header
        }
        print(f"Fetching match ID for Results Vault from URL: {self.results_vault_match_id_url}")
        response = requests.get(self.results_vault_match_id_url, headers=headers)
        response.raise_for_status()
        rv_match_id = response.json().get("object_id1")
        print(rv_match_id)
        return rv_match_id

    def results_vault_api_call(self):
        """
        Fetches match data from the Results Vault API.
        This method constructs a GET request to the Results Vault API using a match ID
        obtained from the internal `_get_match_id_results_vault` method. It sets the required
        headers for the request, including authentication and user-agent information, and
        returns the parsed JSON response.
        Returns:
            dict: The JSON response from the Results Vault API containing match data.
        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """

        rv_match_id= self._get_match_id_results_vault()
        results_vault_url = f"https://api-alb.resultsvault.co.uk/rv/130000/matches/{rv_match_id}/?apiid=1002&strmflg=3"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "origin": "https://lightcliffe.play-cricket.com",
            "referer": "https://lightcliffe.play-cricket.com/",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "x-ias-api-request": self.api_header
        }
        response = requests.get(results_vault_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def nv_process_data(self, data):
        """
        Processes cricket match data to extract batting and bowling statistics for the specified team.
        Args:
            data (dict): The match data containing information about teams, innings, batting, and bowling cards.
        Returns:
            tuple: A tuple containing two pandas DataFrames:
                - The first DataFrame contains batting statistics for the specified team.
                - The second DataFrame contains bowling statistics for the specified team.
        The function determines which team in the match corresponds to `self.team_name`, extracts the team number and opposition,
        and then iterates through the innings to collect batting and bowling data relevant to the team.
        """

        batting, bowling = [], []
        match = data.get('Match', {})
        team1 = match.get('Team1Name', '')
        team2 = match.get('Team2Name', '')

        if self.team_name in team1:
            team_number = team1.replace(self.team_name, '').strip()
            opposition = team2
        else:
            team_number = team2.replace(self.team_name, '').strip()
            opposition = team1

        for innings in data.get('Innings', []):
            if innings.get('BattingTeamName') == f"{self.team_name} {team_number}":
                for batsman in innings.get('BattingCard', []):
                    batting.append({
                        "PlayerTeamName": team_number,
                        "OppositionTeamName": opposition,
                        "PlayerName": batsman.get("PlayerName"),
                        "Runs": round(batsman.get("Runs", 0), 2),
                        "Balls": batsman.get("Balls"),
                        "Minutes": batsman.get("Minutes"),
                        "Fours": batsman.get("Fours"),
                        "Sixes": batsman.get("Sixes"),
                        "StrikeRate": batsman.get("StrikeRate"),
                        "HowOut": batsman.get("HowOut"),
                        "IsDismissed": batsman.get("IsDismissed"),
                    })
            else:
                for bowler in innings.get('BowlingCard', []):
                    bowling.append({
                        "PlayerTeamName": team_number,
                        "OppositionTeamName": opposition,
                        "PlayerName": bowler.get("PlayerName"),
                        "Overs": bowler.get("Overs"),
                        "Maidens": bowler.get("Maidens"),
                        "Runs": bowler.get("Runs"),
                        "Wickets": bowler.get("Wickets"),
                        "Economy": bowler.get("Economy"),
                        "Dots": bowler.get("Dots"),
                        "Fours": bowler.get("Fours"),
                        "Sixes": bowler.get("Sixes"),
                        "NoBalls": bowler.get("NoBalls"),
                        "Wides": bowler.get("Wides"),
                    })
        return pd.DataFrame(batting), pd.DataFrame(bowling)


    def results_vault_process_data(self, data):
        """
        Processes match data from the Results Vault API and extracts batting and bowling performance details.
        Args:
            data (dict): A dictionary containing match data, including team and player performance information.
        Returns:
            tuple: A tuple containing two pandas DataFrames:
                - The first DataFrame contains batting performances for the Lightcliffe team, with columns:
                    ["PlayerTeamName", "OppositionTeamName", "PlayerName", "Runs", "Balls", "Minutes", "Fours", "Sixes", "StrikeRate", "HowOut", "IsDismissed"]
                - The second DataFrame contains bowling performances for the opposition team, with columns:
                    ["PlayerTeamName", "OppositionTeamName", "PlayerName", "Overs", "Maidens", "Runs", "Wickets", "Economy", "Dots", "Fours", "Sixes", "NoBalls", "Wides"]
        Notes:
            - The method distinguishes between the Lightcliffe team and the opposition based on `self.team_name`.
            - Player names are mapped using player IDs for consistency.
            - Batting data is collected only for the Lightcliffe team, while bowling data is collected only for the opposition.
        """

        batting, bowling = [], []

        team1 = data.get("home_name", "")
        team2 = data.get("away_name", "")
        
        if self.team_name in team1:
            team_number = team1.replace(self.team_name, "").strip()
            opposition = team2
        else:
            team_number = team2.replace(self.team_name, "").strip()
            opposition = team1


        # Build player ID to full name mapping
            player_id_to_full_name = {}

        for team in data.get("MatchTeams", []):
            for player in team.get("TeamMembers", []):
                full_player_name = player.get("player_name2")
                player_id_to_full_name[player["player_id"]] = full_player_name


        # Process innings
        for team in data.get("MatchTeams", []):
            team_is_lightcliffe = self.team_name in team.get("team_name", "")
            

            for innings in team.get("Innings", []):
                for perf in innings.get("PlayerPerfs", []):
                    player_id = perf.get("player_id")
                    full_player_name = player_id_to_full_name.get(player_id, perf.get("player_name"))
                    if perf.get("__type", "").startswith("Batting") and team_is_lightcliffe:
                        batting.append({
                            "PlayerTeamName": team_number,
                            "OppositionTeamName": opposition,
                            "PlayerName": full_player_name,
                            "Runs": perf.get("runs"),
                            "Balls": perf.get("balls"),
                            "Minutes": perf.get("minutes"),
                            "Fours": perf.get("fours"),
                            "Sixes": perf.get("sixes"),
                            "StrikeRate": perf.get("strike_rate"),
                            "HowOut": perf.get("dismissal_text"),
                            "IsDismissed": perf.get("dismissal_text") not in [None, "", "dnb", "no"]
                        })
                    elif perf.get("__type", "").startswith("Bowling") and not team_is_lightcliffe:
                        overs = perf.get("overs", 0)
                        runs = perf.get("runs", 0)
                        economy = round(runs / overs, 2) if overs else None
                        bowling.append({
                            "PlayerTeamName": team_number,
                            "OppositionTeamName": opposition,
                            "PlayerName": full_player_name,
                            "Overs": overs,
                            "Maidens": perf.get("maidens"),
                            "Runs": runs,
                            "Wickets": perf.get("wickets"),
                            "Economy": economy,
                            "Dots": perf.get("dot_balls"),
                            "Fours": None,
                            "Sixes": None,
                            "NoBalls": perf.get("no_balls"),
                            "Wides": perf.get("wides"),
                        })
        
        return pd.DataFrame(batting), pd.DataFrame(bowling)

    def get_scorecard(self):
        """
        Retrieves the scorecard data by attempting to call the primary API first.
        If the primary API call fails, it falls back to an alternative API.
        Returns:
            dict or Any: The scorecard data retrieved from either the primary or fallback API.
        Raises:
            Exception: Propagates any exceptions not handled by the fallback mechanism.
        """

        try:
            data = self.nv_api_call()
            return data
        except Exception:
            data = self.results_vault_api_call()
            return data

    def process_data(self, data):
        """
        Processes the input data and delegates to the appropriate processing method based on the data's content.
        Args:
            data (dict): The input data to be processed.
        Returns:
            tuple: A tuple containing two pandas DataFrames. The specific DataFrames returned depend on the data content:
                - If "Match" is in data, returns the result of nv_process_data(data).
                - If "MatchTeams" is in data, returns the result of results_vault_process_data(data).
                - Otherwise, returns two empty DataFrames.
        """
        
        if "Match" in data:
            return self.nv_process_data(data)
        elif "MatchTeams" in data:
            return self.results_vault_process_data(data)
        else:
            return pd.DataFrame(), pd.DataFrame()


if __name__ == "__main__":

    batting_table = pd.DataFrame()
    bowling_table = pd.DataFrame()
    all_batting_dfs = []
    all_bowling_dfs = []
    match_numbers = {
        '7126243'
        }
    team_name = "Lightcliffe CC"

    for match_number in match_numbers:
        scraper = ScorecardAPICall(match_number, team_name)

        try:
            data = scraper.nv_api_call()
            if not data or "Match" not in data:
                raise ValueError("NV API returned no data or missing 'Match' key")
            if not data.get("Innings"):
                raise ValueError("NV API returned data with empty 'Innings' key")
        except Exception:
            try:
                data = scraper.results_vault_api_call()
                if not data or "MatchTeams" not in data:
                    raise ValueError("Results Vault API returned no data or missing 'MatchTeams' key")
            except Exception as e:
                continue

        batting_df, bowling_df = scraper.process_data(data)
        all_batting_dfs.append(batting_df)
        all_bowling_dfs.append(bowling_df)

    if all_batting_dfs:
        batting_table = pd.concat(all_batting_dfs, ignore_index=True)
    if all_bowling_dfs:
        bowling_table = pd.concat(all_bowling_dfs, ignore_index=True)
    

    
    
    print("Batting DataFrame:")
    print(batting_table)
    print("\nBowling DataFrame:")
    print(bowling_table)
    print("Data processing complete.")