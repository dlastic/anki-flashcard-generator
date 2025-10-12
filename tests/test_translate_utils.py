from unittest.mock import MagicMock, patch

import pytest

from translate_utils import (
    TranslationError,
    TranslationItem,
    TranslationResponse,
    translate_sentences,
)


def test_translate_sentences_openai_success():
    sentences = ["This is a **test** sentence."]

    mock_response = MagicMock()
    mock_response.output_parsed = TranslationResponse(
        translations=[
            TranslationItem(
                words_source="test1, test2",
                sentence_source="Toto je **testovacia** veta.",
                sentence_target="This is a **test** sentence.",
            )
        ]
    )

    with patch("openai.OpenAI") as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.responses.parse.return_value = mock_response

        result = translate_sentences(
            sentences=sentences, source_lang="Slovak", api="openai"
        )

    assert isinstance(result, list)
    assert result[0].words_source == "test1, test2"
    assert result[0].sentence_source == "Toto je **testovacia** veta."


def test_translate_sentences_openai_empty_output():
    sentences = ["Test **word**"]

    mock_response = MagicMock()
    mock_response.output_parsed = TranslationResponse(translations=[])

    with patch("openai.OpenAI") as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.responses.parse.return_value = mock_response

        with pytest.raises(TranslationError, match="empty output"):
            translate_sentences(sentences=sentences, api="openai")


def test_translate_sentences_gemini_success():
    sentences = ["This is a **test** sentence."]

    mock_response = MagicMock()
    mock_response.parsed = TranslationResponse(
        translations=[
            TranslationItem(
                words_source="test1, test2",
                sentence_source="Toto je **testovacia** veta.",
                sentence_target="This is a **test** sentence.",
            )
        ]
    )

    with patch("google.genai.Client") as MockGenaiClient:
        mock_client = MockGenaiClient.return_value
        mock_client.models.generate_content.return_value = mock_response

        result = translate_sentences(
            sentences=sentences, source_lang="Slovak", api="gemini"
        )

    assert isinstance(result, list)
    assert result[0].words_source == "test1, test2"
    assert result[0].sentence_source == "Toto je **testovacia** veta."


def test_translate_sentences_gemini_empty_output():
    sentences = ["Test **word**"]

    mock_response = MagicMock()
    mock_response.parsed = TranslationResponse(translations=[])

    with patch("google.genai.Client") as MockGenaiClient:
        mock_client = MockGenaiClient.return_value
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(TranslationError, match="empty output"):
            translate_sentences(sentences=sentences, api="gemini")


def test_translate_sentences_empty_sentences():
    with pytest.raises(
        TranslationError, match="No sentences provided for translation."
    ):
        translate_sentences(sentences=[])


def test_translate_sentences_unsupported_api():
    with pytest.raises(TranslationError, match="Unsupported translation API"):
        translate_sentences(sentences=["Test"], api="unsupported")
