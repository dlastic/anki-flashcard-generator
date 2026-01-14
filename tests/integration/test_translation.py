import os

import pytest

from flashcards.translation import (
    TranslationError,
    TranslationItem,
    translate_sentences,
)

API_KEYS = [
    ("gemini", "GEMINI_API_KEY"),
    ("openai", "OPENAI_API_KEY"),
]
REQUIRED_API_KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY"]
SAMPLE_SENTENCES = [
    "Parler plusieurs langues est un vrai **avantage**.",
    "Les films étrangers rendent l’apprentissage plus **vivant**.",
    "L’allemand est **difficile**, mais fascinant.",
]


@pytest.fixture(scope="session", autouse=True)
def check_api_keys():
    missing = [key for key in REQUIRED_API_KEYS if os.getenv(key) is None]
    if missing:
        pytest.exit(f"Missing required API keys: {', '.join(missing)}")


class TestTranslateSentences:
    @pytest.mark.parametrize("api, env_var", API_KEYS)
    def test_raises_on_missing_api_key(self, api, env_var, monkeypatch):
        monkeypatch.delenv(env_var, raising=False)
        with pytest.raises(TranslationError, match="Missing API key"):
            translate_sentences(sentences=SAMPLE_SENTENCES, api=api)

    @pytest.mark.parametrize("api, env_var", API_KEYS)
    def test_raises_on_invalid_api_key(self, api, env_var, monkeypatch):
        monkeypatch.setenv(env_var, "invalid_key")
        with pytest.raises(TranslationError):
            translate_sentences(sentences=SAMPLE_SENTENCES, api=api)

    @pytest.mark.parametrize("api, env_var", API_KEYS)
    def test_returns_valid_response(self, api, env_var):
        response = translate_sentences(sentences=SAMPLE_SENTENCES, api=api)
        assert isinstance(response, list)
        assert len(response) == len(SAMPLE_SENTENCES)
        assert all(isinstance(item, TranslationItem) for item in response)
