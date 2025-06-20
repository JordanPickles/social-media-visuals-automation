
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import pandas as pd


class PerformanceImageGenerator:
    """
    A class to generate cricket performance images for top batters and bowlers.
    Attributes:
        top_6_batters (pd.DataFrame): DataFrame containing the top 6 batters' performance data.
        top_6_bowlers (pd.DataFrame): DataFrame containing the top 6 bowlers' performance data.
    Methods:
        _get_last_saturday_date():
            Returns the date string of the most recent Saturday in the format "dd Mmm yyyy".
        game_week_image(img):
            Draws the current game week number on the provided image based on the date range.
        generate_batting_image(image_path="Batting Performances Blank Template.png", font_path="Outfit-Bold.ttf"):
            Generates and saves an image displaying the top 6 batting performances, including player names, scores, balls faced, sponsors, and opposition details.
        generate_bowling_image(image_path="Bowling Performances Blank Template.png", font_path="Outfit-Bold.ttf"):
            Generates and saves an image displaying the top 6 bowling performances, including player names, bowling figures, sponsors, and opposition details.
    """

    def __init__(self, top_6_batters: pd.DataFrame, top_6_bowlers: pd.DataFrame):
        self.top_6_batters = top_6_batters
        self.top_6_bowlers = top_6_bowlers

    def _get_last_saturday_date(self):
        """
        Returns the date of the most recent Saturday as a formatted string.
        The function calculates how many days have passed since the last Saturday
        (where Saturday is considered weekday 5), subtracts that from today's date,
        and returns the result formatted as "DD Mon YYYY".
        Returns:
            str: The date of the last Saturday in the format "DD Mon YYYY".
        """

        days_since_saturday = (datetime.today().weekday() - 5) % 7
        return (datetime.today() - timedelta(days=days_since_saturday)).strftime("%d %b %Y")

    def game_week_image(self, img):
        """
        Draws the current game week number onto the provided image.
        The game week is calculated as the number of weeks elapsed since a fixed start date ("25/04/2025")
        up to the most recent Saturday, as determined by the `_get_last_saturday_date` method.
        The text "Game Week {game_week}" is rendered onto the image at a fixed position with a specific font and color.
        Args:
            img (PIL.Image.Image): The image object to draw the game week text onto.
        Returns:
            None: The function modifies the image in place.
        """

        date = self._get_last_saturday_date()
        start_date = datetime.strptime("25/04/2025", "%d/%m/%Y")
        end_date = datetime.strptime(date, "%d %b %Y")
        game_week = ((end_date - start_date).days // 7) + 1

        draw = ImageDraw.Draw(img)
        font_size = 40
        text_color = (203, 144, 14)
        font = ImageFont.truetype("Outfit-Bold.ttf", font_size)
        draw.text((143, 280), f"Game Week {game_week}", fill=text_color, font=font)


    def generate_batting_image(self, image_path="Batting Performances Blank Template.png", font_path="Outfit-Bold.ttf"):
        """
        Generates a batting performance image for the top 6 batters and saves it to disk.
        This method loads a template image, overlays batting statistics for the top 6 batters,
        and saves the resulting image with a filename that includes the date of the last Saturday.
        The statistics displayed for each batter include their name, runs scored (with an asterisk if not dismissed),
        balls faced, sponsor name, and the match-up (team vs opposition). The text is positioned and styled
        according to predefined coordinates and font settings.
        Args:
            image_path (str, optional): Path to the template image file. Defaults to "Batting Performances Blank Template.png".
            font_path (str, optional): Path to the primary font file. Defaults to "Outfit-Bold.ttf".
        Returns:
            None
        Side Effects:
            - Saves the generated image to disk with a filename in the format "Batting_Performances_{date}.png".
            - Prints an error message if the template image cannot be opened.
            - Prints a confirmation message with the output file path upon successful image generation.
        """

        date = self._get_last_saturday_date()
        output_path = f"Batting_Performances_{date}.png"
        try:
            img = Image.open(image_path)
        except Exception as e:
            print(f"Error opening image: {e}")
            return

        draw = ImageDraw.Draw(img)
        self.game_week_image(img)

        num_entries = len(self.top_6_batters)
        start_y = 374
        end_y = 1289
        x_base = 143
        y_positions = [int(start_y + i * (end_y - start_y) / (num_entries - 1)) for i in range(num_entries)]

        for i in range(num_entries):
            name_text = f" |  {self.top_6_batters['PlayerName'].values[i]}"

            score_text = f"{str(round(self.top_6_batters['Runs'].values[i]))}{'*' if not self.top_6_batters['IsDismissed'].values[i] else ''}"
            balls_text = f"({round(self.top_6_batters['Balls'].values[i]):.0f})"
            sponsor_name = f" - {self.top_6_batters['Sponsor Name'].values[i]}"
            oppo_name = f"{self.top_6_batters['PlayerTeamName'].values[i]} vs {self.top_6_batters['OppositionTeamName'].values[i]}"

            y = y_positions[i]
            score_position = (x_base, y)

            font_size = 50
            text_color = (255, 255, 255)
            font = ImageFont.truetype(font_path, font_size)
            bbox = font.getbbox(score_text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            score_text_end_x = score_position[0] + text_width

            draw.text(score_position, score_text, fill=text_color, font=font)

            font_size_balls = 30
            font_balls = ImageFont.truetype(font_path, font_size_balls)
            balls_position = (int(score_text_end_x) + 20, y + 20)
            draw.text(balls_position, balls_text, fill=text_color, font=font_balls)

            bbox = font.getbbox(balls_text)
            text_width = bbox[2] - bbox[0]
            balls_text_end_x = balls_position[0] + text_width

            font_size_name = 50
            font_name = ImageFont.truetype(font_path, font_size_name)
            name_position = (int(balls_text_end_x) - 20, y)
            draw.text(name_position, name_text, fill=text_color, font=font_name)

            bbox = font.getbbox(name_text)
            text_width = bbox[2] - bbox[0]
            name_text_end_x = name_position[0] + text_width

            font_size_sponsor_name = 30
            sponsor_font_path = font_path if sponsor_name.strip().lower() != "- available to sponsor" else "Outfit-Light.ttf"
            sponsor_name_font = ImageFont.truetype(sponsor_font_path, font_size_sponsor_name)
            sponsor_position = (int(name_text_end_x), y + 20)
            draw.text(sponsor_position, sponsor_name, fill=text_color, font=sponsor_name_font)

            font_size_oppo_name = 30
            oppo_name_font = ImageFont.truetype("Outfit-Light.ttf", font_size_oppo_name)
            oppo_position = (x_base, y + 70)
            draw.text(oppo_position, oppo_name, fill=text_color, font=oppo_name_font)

        img.save(output_path)
        print(f"Image saved as {output_path}")

    def generate_bowling_image(self, image_path="Bowling Performances Blank Template.png", font_path="Outfit-Bold.ttf"):
        """
        Generates a bowling performance image for the top 6 bowlers and saves it to disk.
        This method overlays bowler statistics, sponsor information, and match details onto a template image.
        The output image is saved with a filename that includes the date of the last Saturday.
        Args:
            image_path (str, optional): Path to the template image file. Defaults to "Bowling Performances Blank Template.png".
            font_path (str, optional): Path to the primary font file used for text rendering. Defaults to "Outfit-Bold.ttf".
        Side Effects:
            - Saves the generated image to disk with a filename in the format "Bowling_Performances_{date}.png".
            - Prints status messages to the console.
        Notes:
            - Requires the following instance attributes:
                - self.top_6_bowlers: A DataFrame containing columns 'PlayerName', 'Wickets', 'Runs', 'Sponsor Name', 'PlayerTeamName', and 'OppositionTeamName'.
                - self._get_last_saturday_date(): A method that returns the date string for the last Saturday.
                - self.game_week_image(img): A method that draws additional information onto the image.
            - Uses the Pillow library for image manipulation.
            - If the sponsor name is "- Available to Sponsor", a lighter font is used for the sponsor text.
        """
        
        date = self._get_last_saturday_date()
        output_path = f"Bowling_Performances_{date}.png"
        try:
            img = Image.open(image_path)
        except Exception as e:
            print(f"Error opening image: {e}")
            return

        draw = ImageDraw.Draw(img)
        self.game_week_image(img)
        num_entries = len(self.top_6_bowlers)
        start_y = 374
        end_y = 1289
        x_base = 143
        y_positions = [int(start_y + i * (end_y - start_y) / (num_entries - 1)) for i in range(num_entries)]

        for i in range(num_entries):
            name_text = f" |  {self.top_6_bowlers['PlayerName'].values[i]}"
            figures_text = f"{str(self.top_6_bowlers['Wickets'].values[i])}-{str(self.top_6_bowlers['Runs'].values[i])}"
            sponsor_name = f" - {self.top_6_bowlers['Sponsor Name'].values[i]}"
            oppo_name = f"{self.top_6_bowlers['PlayerTeamName'].values[i]} vs {self.top_6_bowlers['OppositionTeamName'].values[i]}"

            y = y_positions[i]
            figures_position = (x_base, y)

            font_size = 50
            text_color = (255, 255, 255)
            font = ImageFont.truetype(font_path, font_size)
            bbox = font.getbbox(figures_text)
            text_width = bbox[2] - bbox[0]
            figures_text_end_x = figures_position[0] + text_width

            draw.text(figures_position, figures_text, fill=text_color, font=font)

            font_size_name = 50
            font_name = ImageFont.truetype(font_path, font_size_name)
            name_position = (int(figures_text_end_x), y)
            draw.text(name_position, name_text, fill=text_color, font=font_name)

            bbox = font.getbbox(name_text)
            text_width = bbox[2] - bbox[0]
            name_text_end_x = name_position[0] + text_width

            font_size_sponsor_name = 30
            sponsor_font_path = font_path if sponsor_name.strip().lower() != "- available to sponsor" else "Outfit-Light.ttf"
            sponsor_name_font = ImageFont.truetype(sponsor_font_path, font_size_sponsor_name)
            sponsor_position = (int(name_text_end_x), y + 20)
            draw.text(sponsor_position, sponsor_name, fill=text_color, font=sponsor_name_font)

            font_size_oppo_name = 30
            oppo_name_font = ImageFont.truetype("Outfit-Light.ttf", font_size_oppo_name)
            oppo_position = (x_base, y + 70)
            draw.text(oppo_position, oppo_name, fill=text_color, font=oppo_name_font)

        img.save(output_path)
        print(f"Image saved as {output_path}")

