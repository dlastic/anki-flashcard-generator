from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def translate_sentences_chatgpt(sentences: str | None) -> str:
    """Translate sentence using ChatGPT."""
    if not sentences:
        return "There are no sentences in the page."

    instructions = """
    You are a professional translator. For each sentence provided in the input list (sentences are separated by newlines), identify the word wrapped in <u>...</u> tags. Translate that underlined word into natural English in the context of the full sentence. If a one-word translation is not possible, use multiple words or a short phrase that best captures the meaning.

    Also translate the entire sentence into English, and wrap the translated word in <u>...</u> tags.

    Return your result as a valid JSON array of arrays, each with two strings:
    1. The translated underlined word (or multiple words, or short phrase, context-aware).
    2. The full sentence translated into English.

    Return only raw JSON, without enclosing it in triple quotes or markdown formatting.
    """.strip()

    client = OpenAI()
    response = client.responses.create(
        model="o4-mini",
        instructions=instructions,
        input=sentences,
    )

    return response.output_text
