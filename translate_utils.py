from typing import cast

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
You are a professional translator. For each sentence provided in the input list (sentences are separated by newlines), identify the word wrapped in **...** tags. Translate that bold word into natural {source_lang} in the context of the full sentence. If the word is a slang term, provide an equivalent slang term in {source_lang}. If a one-word translation is not possible, use multiple words or a short phrase that best captures the meaning. Always provide two similar translations for the bold word, separated by a comma followed by a space (, ), and ensure both translations are in lowercase.

Also translate the entire sentence into {source_lang}, and wrap the translated word in **...** tags.

Your response must be a valid JSON object with a single property "translations", which is an array of objects. Each object must have the following properties:

{{
  "words_source": "first translation, second translation of the **bold** word in lowercase",
  "sentence_source": "full translated sentence with **bold** word",
  "sentence_target": "original sentence with **bold** word"
}}
""".strip()


def _build_instructions(source_lang: str) -> str:
    return _translation_instructions_template.format(source_lang=source_lang)


def translate_sentences(
    sentences: list[str], source_lang: str = "English", api: str = "gemini"
) -> list[TranslationItem]:
    """Translate sentence using LLM."""
    if not sentences:
        raise TranslationError("No sentences provided for translation.")
    instructions = _build_instructions(source_lang)
    sentences_str = "\n".join(sentences)

    if api == "openai":
        from openai import OpenAI

        client = OpenAI()
        response = client.responses.parse(
            model="gpt-4o",
            instructions=instructions,
            input=sentences_str,
            text_format=TranslationResponse,
        )

        parsed = response.output_parsed
        if not parsed or not parsed.translations:
            raise TranslationError("Translation service returned empty output.")

        return parsed.translations

    if api == "gemini":
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

        # Cast the response to the expected type (Gemini SDK doesn't
        # provide precise typing for `.parsed`)
        parsed = cast(TranslationResponse, response.parsed)
        if not parsed or not parsed.translations:
            raise TranslationError("Translation service returned empty output.")

        return parsed.translations

    raise TranslationError(f"Unsupported translation API: {api}")
