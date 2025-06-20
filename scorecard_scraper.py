from bs4 import BeautifulSoup
import requests
import re
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import time


class MatchIDExtractor:
    """
    MatchIDExtractor is a utility class for extracting cricket match IDs and specific API headers from the Lightcliffe Play-Cricket website.
    Attributes:
        url (str): The URL of the page to scrape for match IDs.
        headers (dict): HTTP headers used for fetching HTML content.
    Methods:
        fetch_html():
            Fetches the HTML content of the provided URL using HTTP GET.
            Returns:
                str: The HTML content of the page.
        extract_match_ids(html):
            Parses the provided HTML to extract match IDs for matches involving "Lightcliffe".
            Args:
                html (str): The HTML content to parse.
            Returns:
                list[str]: A list of extracted match IDs as strings.
        get_match_ids():
            Fetches the HTML content from the URL and extracts match IDs.
            Returns:
                list[str]: A list of extracted match IDs.
        get_ias_api_header_from_match_page(match_id):
            Launches a headless Chrome browser to load the match results page and inspects network requests to extract the "x-ias-api-request" header.
            Args:
                match_id (str): The match ID to construct the match results page URL.
            Returns:
                str or None: The value of the "x-ias-api-request" header if found, otherwise None.
    """

    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        }

    def fetch_html(self):
        """
        Fetches the HTML content from the specified URL using HTTP GET request.
        Returns:
            str: The HTML content of the requested page.
        Raises:
            requests.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        return response.text

    def extract_match_ids(self, html):
        """
        Extracts match IDs from the provided HTML content for matches involving "Lightcliffe".
        Parses the HTML to find all div elements with class "row". For each such div, it checks if the text contains "Lightcliffe".
        If so, it looks for an anchor tag with class "link-scorecard" and extracts the match ID from its href attribute using a regular expression.
        Args:
            html (str): The HTML content as a string.
        Returns:
            list: A list of match ID strings extracted from the HTML.
        """

        soup = BeautifulSoup(html, "html.parser")
        match_ids = []

        for match_div in soup.find_all("div", class_="row"):
            if "Lightcliffe" not in match_div.get_text():
                continue

            scorecard_link = match_div.find("a", class_="link-scorecard", href=True)
            if scorecard_link:
                href = scorecard_link["href"]
                match = re.search(r'/website/results/(\d+)', href)
                if match:
                    match_ids.append(match.group(1))

        return match_ids

    def get_match_ids(self):
        """
        Retrieves match IDs by fetching and parsing the HTML content.
        Returns:
            list: A list of match IDs extracted from the HTML.
        Raises:
            Exception: If fetching or extracting match IDs fails.
        """

        html = self.fetch_html()
        return self.extract_match_ids(html)

    def get_ias_api_header_from_match_page(self, match_id):
        """
        Retrieves the value of the 'x-ias-api-request' header from network requests made when loading a match results page.
        Args:
            match_id (str or int): The unique identifier for the match whose results page will be loaded.
        Returns:
            str or None: The value of the 'x-ias-api-request' header if found in any network request, otherwise None.
        Notes:
            - This method uses Selenium WebDriver to load the match page in a headless Chrome browser.
            - It waits for 8 seconds to allow JavaScript and XHR requests to complete.
            - Requires Selenium and a compatible ChromeDriver installed.
            - Assumes the WebDriver instance supports capturing network requests (e.g., via selenium-wire).
        """
    
        match_url = f"https://lightcliffe.play-cricket.com/website/results/{match_id}"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(match_url)

        time.sleep(8)  # Allow time for JavaScript/XHR requests to fire

        header_value = None

        for request in driver.requests:
            if request.response and "x-ias-api-request" in request.headers:
                print(f"Matched URL: {request.url}")
                header_value = request.headers.get("x-ias-api-request")
                break

        driver.quit()
        return header_value


if __name__ == "__main__":
    url = "https://lightcliffe.play-cricket.com/Matches?tab=WeeklyResult&team_id=&view_by=month&team_id=&search_in=&q%5Bcategory_id%5D=1&q%5Bgender_id%5D=all&home_or_away=both&commit=Apply"
    extractor = MatchIDExtractor(url)

    match_ids = extractor.get_match_ids()
    print("Extracted Match IDs:", match_ids)

    if match_ids:
        api_header = extractor.get_ias_api_header_from_match_page(match_ids[0])
        print("x-ias-api-request Header:", api_header)
    else:
        print("No match IDs found.")
