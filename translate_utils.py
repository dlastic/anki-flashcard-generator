import os

import deepl
from dotenv import load_dotenv

load_dotenv()


def translate_sentence_deepl(sentence: str, target_lang: str):
    """Translate sentence using DeepL translator"""
    DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
    if not DEEPL_API_KEY:
        raise NameError("The API_KEY not found")
    translator = deepl.Translator(DEEPL_API_KEY)
    result = translator.translate_text(sentence, target_lang=target_lang)

    return result.text


print(
    translate_sentence_deepl(
        "Elle est sortie de l'hôpital, mais elle doit y retourner la semaine prochaine pour refaire le pansement.",
        "en-us",
    )
)
