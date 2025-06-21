import os

import deepl
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def translate_sentence_deepl(sentence: str, target_lang: str):
    """Translate sentence using DeepL translator"""
    DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
    if not DEEPL_API_KEY:
        raise NameError("The API_KEY not found")
    translator = deepl.Translator(DEEPL_API_KEY)
    result = translator.translate_text(sentence, target_lang=target_lang)

    return result.text  # type: ignore


def translate_sentence_chatgpt(sentence: str) -> str:
    """Translate sentence using ChatGPT"""
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="Translate the following sentence to English. Respond with only the translated sentence.",
        input=sentence,
    )

    return response.output_text


print(
    translate_sentence_chatgpt(
        "Das erkennst du an ihrem Gang? Wow."
    )
)
