from dotenv import load_dotenv
from pydantic import BaseModel


class TranslationError(Exception):
    pass


class TranslationItem(BaseModel):
    words_source: str
    sentence_source: str
    sentence_target: str


class TranslationResponse(BaseModel):
    translations: list[TranslationItem]


load_dotenv()

_translation_instructions_template = """
You are a professional translator. For each sentence provided in the input list (sentences are separated by newlines), identify the word wrapped in <u>...</u> tags. Translate that underlined word into natural {source_lang} in the context of the full sentence. If the word is a slang term, provide an equivalent slang term in {source_lang}. If a one-word translation is not possible, use multiple words or a short phrase that best captures the meaning. Always provide two similar translations for the underlined word, separated by a comma followed by a space (, ).

Also translate the entire sentence into {source_lang}, and wrap the translated word in <u>...</u> tags.

Your response must be a valid JSON object with a single property "translations", which is an array of objects. Each object must have the following properties:

{{
  "words_source": "first translation, second translation of the underlined word",
  "sentence_source": "full translated sentence with <u>underlined word</u>",
  "sentence_target": "original sentence with <u>underlined word</u>"
}}
""".strip()


def _build_instructions(source_lang: str) -> str:
    return _translation_instructions_template.format(source_lang=source_lang)


def translate_sentences_chatgpt(
    sentences: list[str], source_lang="Slovak"
) -> list[TranslationItem]:
    """Translate sentence using ChatGPT."""
    if not sentences:
        raise TranslationError("No sentences provided for translation.")
    instructions = _build_instructions(source_lang)
    sentences_str = "\n".join(sentences)

    from openai import OpenAI, OpenAIError

    try:
        client = OpenAI()
        response = client.responses.parse(
            model="gpt-4o",
            instructions=instructions,
            input=sentences_str,
            text_format=TranslationResponse,
        )
    except OpenAIError as e:
        try:
            error_message = e.response.json()["error"]["message"]
        except Exception:
            error_message = str(e)
        raise TranslationError(error_message) from e

    if not response or not response.output_parsed:
        raise TranslationError("Translation service returned empty output.")

    return response.output_parsed.translations


def translate_sentences_gemini(
    sentences: list[str], source_lang="Slovak"
) -> list[TranslationItem]:
    """Translate sentence using Google Gemini."""
    if not sentences:
        raise TranslationError("No sentences provided for translation.")
    instructions = _build_instructions(source_lang)
    sentences_str = "\n".join(sentences)

    from google import genai
    from google.genai import types

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=sentences_str,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction=instructions,
            response_mime_type="application/json",
            response_schema=TranslationResponse,
        ),
    )

    if not response or not response.parsed:
        raise TranslationError("Translation service returned empty output.")

    return response.parsed.translations
