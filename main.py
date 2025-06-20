import pandas as pd
from scorecard_api import ScorecardAPICall
from data_processing import SponsorDataProcessor
from bs4 import BeautifulSoup
from image_generation import PerformanceImageGenerator
from scorecard_scraper import MatchIDExtractor


def main(team_name):
    """
    Main function to extract, process, and visualize cricket match data for a given team.
    This function performs the following steps:
    1. Extracts match IDs from the Lightcliffe Play-Cricket website.
    2. Fetches match data for each match ID using two different APIs (NV API and Results Vault API) with error handling.
    3. Processes the fetched data to generate batting and bowling DataFrames for each match.
    4. Concatenates all match DataFrames into comprehensive batting and bowling tables.
    5. Loads sponsor data and determines the top 6 batters and bowlers using the SponsorDataProcessor.
    6. Generates performance images for the top 6 batters and bowlers using the PerformanceImageGenerator.
    Args:
        team_name (str): The name of the cricket team for which data is to be processed.
    Returns:
        tuple: A tuple containing two lists:
            - top_6_batters (list): List of top 6 batters based on processed data.
            - top_6_bowlers (list): List of top 6 bowlers based on processed data.
    """


    all_batting_dfs = []
    all_bowling_dfs = []

    # Initialise the MatchIDExtractor with the URL and get match IDs
    extractor = MatchIDExtractor("https://lightcliffe.play-cricket.com/Matches?tab=WeeklyResult&team_id=&view_by=month&team_id=&search_in=&q%5Bcategory_id%5D=1&q%5Bgender_id%5D=all&home_or_away=both&commit=Apply")
    match_numbers = extractor.get_match_ids()
    api_header = extractor.get_ias_api_header_from_match_page(match_numbers[0])
    

    # Loop through each match number and fetch data using ScorecardAPICall
    for match_number in match_numbers:
        scraper = ScorecardAPICall(match_number, team_name, api_header)
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
                print(f"Failed to fetch data for {match_number}: {e}")
                continue

        batting_df, bowling_df = scraper.process_data(data)
        all_batting_dfs.append(batting_df)
        all_bowling_dfs.append(bowling_df)

    if all_batting_dfs:
        batting_table = pd.concat(all_batting_dfs, ignore_index=True)
    if all_bowling_dfs:
        bowling_table = pd.concat(all_bowling_dfs, ignore_index=True)
    print(batting_table)

    # Initialise the SponsorDataProcessor with the combined batting and bowling tables
    sponsor_data_processor = SponsorDataProcessor(batting_table, bowling_table)
    sponsor_data_processor.load_sponsor_data()
    top_6_batters, top_6_bowlers = sponsor_data_processor.data_wrangling()

    # Initialise and call the modules in the PerformanceImageGenerator class
    performance_generator = PerformanceImageGenerator(top_6_batters, top_6_bowlers)
    print("Top 6 Batters:", top_6_batters)
    print("Top 6 Bowlers:", top_6_bowlers)
    performance_generator.generate_batting_image()
    performance_generator.generate_bowling_image()
    return top_6_batters, top_6_bowlers

if __name__ == "__main__":
    team_name = "Lightcliffe CC"

    top_6_batters, top_6_bowlers = main(team_name)


