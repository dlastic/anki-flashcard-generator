import pytest
from unittest.mock import patch, MagicMock
from openai import OpenAIError

from translate_utils import translate_sentences_chatgpt, TranslationError


def test_translate_sentences_chatgpt_success():
    sentences = ["This is a <u>test</u> sentence."]

    mock_response = MagicMock()
    mock_response.output_text = '[["test1, test2", "Toto je <u>test</u> veta."]]'

    with patch("translate_utils.OpenAI") as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.responses.create.return_value = mock_response

        result = translate_sentences_chatgpt(sentences, source_lang="Slovak")

    # Check that the result matches the mocked output_text
    assert result == mock_response.output_text
    # Check the client was called with expected args (partial check)
    called_args = mock_client.responses.create.call_args[1]
    assert "gpt-4o" == called_args["model"]
    assert "Slovak" in called_args["instructions"]
    assert "\n".join(sentences) == called_args["input"]


def test_translate_sentences_chatgpt_empty_sentences():
    with pytest.raises(TranslationError, match="No sentences provided"):
        translate_sentences_chatgpt([])


def test_translate_sentences_chatgpt_openai_error_with_json_message():
    sentences = ["Test <u>word</u>"]

    class DummyResponse:
        def json(self):
            return {"error": {"message": "API failure"}}

    error = OpenAIError()
    error.response = DummyResponse()

    with patch("translate_utils.OpenAI") as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.responses.create.side_effect = error

        with pytest.raises(TranslationError, match="API failure"):
            translate_sentences_chatgpt(sentences)


def test_translate_sentences_chatgpt_openai_error_without_json_message():
    sentences = ["Test <u>word</u>"]

    error = OpenAIError("Some error occurred")
    error.response = None  # no response or json method

    with patch("translate_utils.OpenAI") as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.responses.create.side_effect = error

        with pytest.raises(TranslationError, match="Some error occurred"):
            translate_sentences_chatgpt(sentences)


def test_translate_sentences_chatgpt_empty_output_text():
    sentences = ["Test <u>word</u>"]

    mock_response = MagicMock()
    mock_response.output_text = ""

    with patch("translate_utils.OpenAI") as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.responses.create.return_value = mock_response

        with pytest.raises(TranslationError, match="empty output"):
            translate_sentences_chatgpt(sentences)
