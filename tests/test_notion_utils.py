from unittest.mock import patch

import pytest

from notion_utils import extract_page_title, format_rich_text, get_page_id

DUMMY_PAGE_ID = "1234abcd5678efgh"


def test_extract_page_title_normal_case():
    mock_result = {
        "properties": {
            "Name": {"type": "title", "title": [{"plain_text": "Test Page Title"}]}
        }
    }

    assert extract_page_title(mock_result) == "Test Page Title"


def test_extract_page_title_missing_title():
    mock_result = {
        "properties": {
            "Name": {"type": "rich_text", "rich_text": [{"plain_text": "Not a title"}]}
        }
    }

    assert extract_page_title(mock_result) is None


def test_extract_page_title_empty_properties():
    mock_result = {"properties": {}}

    assert extract_page_title(mock_result) is None


def test_extract_page_title_no_properties():
    mock_result = {}

    assert extract_page_title(mock_result) is None


def test_get_page_id_exact_match():
    mock_response = {
        "results": [
            {
                "id": DUMMY_PAGE_ID,
                "properties": {
                    "Name": {"type": "title", "title": [{"plain_text": "My Test Page"}]}
                },
            }
        ]
    }

    with patch("notion_utils.notion.search", return_value=mock_response):
        result = get_page_id("My Test Page")
        assert result == DUMMY_PAGE_ID


def test_get_page_id_no_match():
    mock_response = {
        "results": [
            {
                "id": "irrelevant-id",
                "properties": {
                    "Name": {"type": "title", "title": [{"plain_text": "Another Page"}]}
                },
            }
        ]
    }

    with patch("notion_utils.notion.search", return_value=mock_response):
        result = get_page_id("Nonexistent Page")
        assert result is None


def test_get_page_id_invalid_type():
    with pytest.raises(TypeError):
        get_page_id(123)  # type: ignore


def test_format_rich_text_basic():
    mock_rich_text = [
        {"plain_text": "Hello ", "annotations": {"underline": False}},
        {"plain_text": "World", "annotations": {"underline": True}},
    ]

    result = format_rich_text(mock_rich_text)
    assert result == "Hello <u>World</u>"


def test_format_rich_text_empty():
    mock_rich_text = []

    result = format_rich_text(mock_rich_text)
    assert result == ""


def test_format_rich_text_no_annotations():
    mock_rich_text = [
        {"plain_text": "Just text without ", "annotations": {"underline": False}},
        {"plain_text": "formatting", "annotations": {"underline": False}},
    ]

    result = format_rich_text(mock_rich_text)
    assert result == "Just text without formatting"
