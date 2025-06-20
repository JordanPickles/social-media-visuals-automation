import os
import openai


class OpenAICaptionGenerator:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key

    def generate_weekly_caption(self, summary_stats: str) -> str:
        prompt = (
            f"Write a fun, informal and engaging cricket match summary caption for social media "
            f"based on the following performance summary:\n\n{summary_stats}\n\n"
            f"Keep it under 280 characters."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=100
        )

        return response['choices'][0]['message']['content'].strip()


if __name__ == "__main__":
    summary_text = "Lightcliffe CC 3rd XI defended 107 runs with standout bowling from J Farr (5-29) and Q Ali (4-20)."
    generator = OpenAICaptionGenerator()
    caption = generator.generate_weekly_caption(summary_text)
    print(caption)

    