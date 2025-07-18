from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


class TranslationError(Exception):
    pass


load_dotenv()


def translate_sentences_chatgpt(sentences: list[str], source_lang="Slovak") -> str:
    """Translate sentence using ChatGPT."""
    if not sentences:
        raise TranslationError("No sentences provided for translation.")
    sentences_str = "\n".join(sentences)

    instructions = f"""
    You are a professional translator. For each sentence provided in the input list (sentences are separated by newlines), identify the word wrapped in <u>...</u> tags. Translate that underlined word into natural {source_lang} in the context of the full sentence. If the word is a slang term, provide an equivalent slang term in {source_lang}. If a one-word translation is not possible, use multiple words or a short phrase that best captures the meaning. Always provide two similar translations for the underlined word, separated by a comma and a space.

    Also translate the entire sentence into {source_lang}, and wrap the translated word in <u>...</u> tags.

    Return your result as a valid JSON array of arrays, each with two strings:
    1. The translations for the underlined word (or multiple words, or short phrase, context-aware).
    2. The full sentence translated into {source_lang}.

    Return only raw JSON, without enclosing it in triple quotes or markdown formatting.
    Format the JSON as compact as possible. Avoid indentation, line breaks, or extra spacing.
    """.strip()

    try:
        client = OpenAI()
        response = client.responses.create(
            model="gpt-4o",
            instructions=instructions,
            input=sentences_str,
        )
    except OpenAIError as e:
        try:
            error_message = e.response.json()["error"]["message"]
        except Exception:
            error_message = str(e)
        raise TranslationError(error_message) from e

    if not response or not response.output_text:
        raise TranslationError("Translation service returned empty output.")

    return response.output_text
