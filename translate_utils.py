from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def translate_sentences_chatgpt(sentences: list[str]) -> str | None:
    """Translate sentence using ChatGPT."""
    if not sentences:
        return None
    sentences_str = "\n".join(sentences)

    instructions = """
    You are a professional translator. For each sentence provided in the input list (sentences are separated by newlines), identify the word wrapped in <u>...</u> tags. Translate that underlined word into natural English in the context of the full sentence. If the word is a slang term, provide an equivalent slang term in English. If a one-word translation is not possible, use multiple words or a short phrase that best captures the meaning. Always provide two similar translations for the underlined word, separated by a comma and a space.

    Also translate the entire sentence into English, and wrap the translated word in <u>...</u> tags.

    Return your result as a valid JSON array of arrays, each with two strings:
    1. The translations for the underlined word (or multiple words, or short phrase, context-aware).
    2. The full sentence translated into English.

    Return only raw JSON, without enclosing it in triple quotes or markdown formatting.
    Format the JSON as compact as possible. Avoid indentation, line breaks, or extra spacing.
    """.strip()

    client = OpenAI()
    response = client.responses.create(
        model="gpt-4o",
        instructions=instructions,
        input=sentences_str,
    )

    return response.output_text
