import os
from abc import ABC, abstractmethod

from pydantic import BaseModel


class TranslationError(Exception):
    pass


class TranslationItem(BaseModel):
    words_source: str
    sentence_source: str
    sentence_target: str


class TranslationResponse(BaseModel):
    translations: list[TranslationItem]


class _LLMAdapter(ABC):
    """Adapter interface for an LLM provider."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model

    @abstractmethod
    def generate(self, instructions: str, input_text: str) -> TranslationResponse:
        """Run the provider and return a parsed TranslationResponse."""
        raise NotImplementedError


class _OpenAIAdapter(_LLMAdapter):
    def generate(self, instructions: str, input_text: str) -> TranslationResponse:
        from openai import APIError, OpenAI

        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if OPENAI_API_KEY is None:
            raise TranslationError("Missing API key for OpenAI API.")

        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.responses.parse(
                model=self.model or "gpt-4o",
                instructions=instructions,
                input=input_text,
                text_format=TranslationResponse,
            )
        except APIError as e:
            message = getattr(e, "body", {}).get("message", str(e))
            raise TranslationError(f"OpenAI API error: {message}") from e

        parsed_response = response.output_parsed
        if not parsed_response or not parsed_response.translations:
            raise TranslationError("Translation service returned empty output.")
        return parsed_response


class _GeminiAdapter(_LLMAdapter):
    def generate(self, instructions: str, input_text: str) -> TranslationResponse:
        from google import genai
        from google.genai import types
        from google.genai.errors import APIError

        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY is None:
            raise TranslationError("Missing API key for Gemini API.")

        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model=self.model or "gemini-3-flash-preview",
                contents=input_text,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    system_instruction=instructions,
                    response_mime_type="application/json",
                    response_schema=TranslationResponse,
                ),
            )
        except APIError as e:
            raise TranslationError(f"Gemini API error: {e.message}") from e

        parsed_response = getattr(response, "parsed", None)
        if not parsed_response or not parsed_response.translations:
            raise TranslationError("Translation service returned empty output.")

        return parsed_response


_ADAPTERS: dict[str, type[_LLMAdapter]] = {}


def _register_adapter(name: str, cls: type[_LLMAdapter]) -> None:
    """Register an adapter class under a provider name."""
    _ADAPTERS[name] = cls


def _get_adapter(name: str, model: str | None = None) -> _LLMAdapter:
    try:
        cls = _ADAPTERS[name]
    except KeyError:
        raise TranslationError(f"Unsupported translation API: {name}")
    return cls(model=model)


_register_adapter("openai", _OpenAIAdapter)
_register_adapter("gemini", _GeminiAdapter)


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
    sentences: list[str],
    source_lang: str = "English",
    api: str = "gemini",
    model: str | None = None,
) -> list[TranslationItem]:
    if not sentences:
        raise TranslationError("No sentences provided for translation.")
    instructions = _build_instructions(source_lang)
    sentences_str = "\n".join(sentences)
    adapter = _get_adapter(api, model=model)
    response = adapter.generate(instructions=instructions, input_text=sentences_str)

    return response.translations
