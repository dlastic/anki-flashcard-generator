from unittest.mock import MagicMock, patch

import pytest

from flashcards.notion_utils import (
    PageEmptyError,
    PageNotFoundError,
    extract_page_title,
    format_rich_text,
    get_page_content,
    get_page_id,
)

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


def test_extract_page_title_missing_or_empty_properties():
    assert extract_page_title({"properties": {}}) is None
    assert extract_page_title({}) is None


def test_get_page_id_exact_match():
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [
            {
                "id": DUMMY_PAGE_ID,
                "properties": {
                    "Name": {"type": "title", "title": [{"plain_text": "My Test Page"}]}
                },
            }
        ]
    }

    result = get_page_id(mock_client, "My Test Page")
    assert result == DUMMY_PAGE_ID
    mock_client.search.assert_called_once()


def test_get_page_id_no_match():
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [
            {
                "id": "irrelevant-id",
                "properties": {
                    "Name": {"type": "title", "title": [{"plain_text": "Another Page"}]}
                },
            }
        ]
    }

    result = get_page_id(mock_client, "Nonexistent Page")
    assert result is None
    mock_client.search.assert_called_once()


def test_format_rich_text_basic():
    mock_rich_text = [
        {"plain_text": "Hello ", "annotations": {"bold": False}},
        {"plain_text": "World", "annotations": {"bold": True}},
    ]

    result = format_rich_text(mock_rich_text)
    assert result == "Hello **World**"


def test_format_rich_text_empty():
    mock_rich_text = []

    result = format_rich_text(mock_rich_text)
    assert result == ""


def test_format_rich_text_no_annotations():
    mock_rich_text = [
        {"plain_text": "Just text without ", "annotations": {"bold": False}},
        {"plain_text": "formatting", "annotations": {"bold": False}},
    ]

    result = format_rich_text(mock_rich_text)
    assert result == "Just text without formatting"


def test_get_page_content_missing_page():
    mock_client = MagicMock()
    with patch("flashcards.notion_utils.get_page_id", return_value=None):
        with pytest.raises(PageNotFoundError):
            get_page_content(mock_client, "Missing Page", count=1)


def test_get_page_content_empty_blocks():
    mock_client = MagicMock()
    mock_client.blocks.children.list.return_value = {
        "results": [
            {
                "type": "paragraph",
                "paragraph": {"rich_text": []},
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"plain_text": "Only line", "annotations": {"bold": False}}
                    ]
                },
            },
        ]
    }
    with patch("flashcards.notion_utils.get_page_id", return_value="dummy_id"):
        with pytest.raises(PageEmptyError):
            get_page_content(mock_client, "Page With Empty Block", count=1)


def test_get_page_content_respects_count_limit():
    mock_client = MagicMock()
    mock_client.blocks.children.list.return_value = {
        "results": [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"plain_text": "First", "annotations": {"bold": True}}
                    ]
                },
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"plain_text": "Second", "annotations": {"bold": True}}
                    ]
                },
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"plain_text": "Third", "annotations": {"bold": True}}
                    ]
                },
            },
        ]
    }

    with patch("flashcards.notion_utils.get_page_id", return_value="dummy_id"):
        result = get_page_content(mock_client, "Limited Page", count=2)
        assert result == ["**First**", "**Second**"]


def test_get_page_content_skips_non_bolded():
    mock_client = MagicMock()
    mock_client.blocks.children.list.return_value = {
        "results": [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "plain_text": "No bold",
                            "annotations": {"bold": False},
                        }
                    ]
                },
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "plain_text": "Yes bold",
                            "annotations": {"bold": True},
                        }
                    ]
                },
            },
        ]
    }

    with patch("flashcards.notion_utils.get_page_id", return_value="dummy_id"):
        result = get_page_content(mock_client, "Mixed Page", count=1)
        assert result == ["**Yes bold**"]


def test_get_page_content_fewer_bolded_than_count():
    mock_client = MagicMock()
    mock_client.blocks.children.list.return_value = {
        "results": [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "One", "annotations": {"bold": True}}]
                },
            }
        ]
    }

    with patch("flashcards.notion_utils.get_page_id", return_value="dummy_id"):
        result = get_page_content(mock_client, "Short Page", count=3)
        assert result == ["**One**"]
