import os

import pytest

from flashcards.translation import (
    TranslationError,
    TranslationItem,
    translate_sentences,
)

APIS = ["gemini", "openai"]
REQUIRED_API_KEYS = ["GEMINI_DEV_API_KEY", "OPENAI_API_KEY"]
APIS_KEYS = list(zip(APIS, REQUIRED_API_KEYS))
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
    @pytest.mark.parametrize("api, env_var", APIS_KEYS)
    def test_raises_on_missing_api_key(self, api, env_var, monkeypatch):
        monkeypatch.delenv(env_var, raising=False)
        with pytest.raises(TranslationError, match="Missing API key"):
            translate_sentences(sentences=SAMPLE_SENTENCES, api=api)

    @pytest.mark.parametrize("api, env_var", APIS_KEYS)
    def test_raises_on_invalid_api_key(self, api, env_var, monkeypatch):
        monkeypatch.setenv(env_var, "invalid_key")
        with pytest.raises(TranslationError):
            translate_sentences(sentences=SAMPLE_SENTENCES, api=api)

    @pytest.mark.parametrize("api", APIS)
    def test_raises_on_invalid_model(self, api):
        with pytest.raises(TranslationError, match="API error"):
            translate_sentences(
                sentences=SAMPLE_SENTENCES,
                api=api,
                model="non_existent_model",
            )

    @pytest.mark.parametrize("api", APIS)
    def test_returns_valid_response(self, api):
        response = translate_sentences(sentences=SAMPLE_SENTENCES, api=api)
        assert isinstance(response, list)
        assert len(response) == len(SAMPLE_SENTENCES)
        assert all(isinstance(item, TranslationItem) for item in response)
