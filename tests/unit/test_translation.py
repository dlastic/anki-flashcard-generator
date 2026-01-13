from unittest.mock import patch

import pytest

from flashcards.translation import (
    TranslationError,
    TranslationItem,
    TranslationResponse,
    _GeminiAdapter,
    _get_adapter,
    _OpenAIAdapter,
    translate_sentences,
)


class TestGetAdapter:
    @pytest.mark.parametrize(
        "api, expected_class, model",
        [
            ("openai", _OpenAIAdapter, "gpt-4"),
            ("openai", _OpenAIAdapter, None),
            ("gemini", _GeminiAdapter, "gemini-2.5-flash"),
            ("gemini", _GeminiAdapter, None),
        ],
    )
    def test_get_adapter(self, api, expected_class, model):
        adapter = _get_adapter(api, model=model)
        assert isinstance(adapter, expected_class)
        assert adapter.model == model

    def test_raises_on_unsupported_adapter(self):
        with pytest.raises(TranslationError, match="Unsupported translation API"):
            _get_adapter("nonexistent")


class TestTranslateSentences:
    def test_returns_translations(self):
        mock_sentences = ["This is a **test** sentence."]
        mock_translation = TranslationItem(
            words_source="test1, test2",
            sentence_source="Toto je **testovacia** veta.",
            sentence_target="This is a **test** sentence.",
        )
        mock_response = TranslationResponse(translations=[mock_translation])

        with patch("flashcards.translation._GeminiAdapter.generate", return_value=mock_response):  # fmt: skip
            result = translate_sentences(sentences=mock_sentences, source_lang="Slovak")
        translation = result[0]

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(translation, TranslationItem)
        assert translation.words_source == "test1, test2"
        assert translation.sentence_source == "Toto je **testovacia** veta."
        assert translation.sentence_target == "This is a **test** sentence."

    def test_raises_on_empty_input(self):
        with pytest.raises(TranslationError, match="No sentences provided"):
            translate_sentences(sentences=[])

    def test_raises_on_unsupported_api(self):
        with pytest.raises(TranslationError, match="Unsupported translation API"):
            translate_sentences(sentences=["Test"], api="unsupported")
