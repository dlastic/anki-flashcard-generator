from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def translate_sentence_chatgpt(sentence: str) -> str:
    """Translate sentence using ChatGPT"""
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="Translate the following sentence to English. Respond with only the translated sentence.",
        input=sentence,
    )

    return response.output_text


print(translate_sentence_chatgpt("Das erkennst du an ihrem Gang? Wow."))
