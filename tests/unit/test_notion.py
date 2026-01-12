from unittest.mock import MagicMock, patch

import pytest

from flashcards.notion import (
    AmbiguousTitleError,
    PageEmptyError,
    PageNotFoundError,
    extract_page_title,
    format_rich_text,
    get_page_content,
    get_page_id,
)


class TestExtractPageTitle:
    def test_success(self):
        mock_result = {
            "properties": {
                "title": {
                    "type": "title",
                    "title": [
                        {
                            "plain_text": "Test Page Title",
                        },
                    ],
                }
            }
        }
        assert extract_page_title(mock_result) == "Test Page Title"

    def test_missing_title(self):
        mock_result = {
            "properties": {
                "title": {
                    "type": "rich_text",
                    "rich_text": [
                        {
                            "plain_text": "Not a title",
                        },
                    ],
                }
            }
        }
        assert extract_page_title(mock_result) is None

    def test_missing_or_empty_properties(self):
        assert extract_page_title({"properties": {}}) is None
        assert extract_page_title({}) is None


class TestFormatRichText:
    def test_basic(self):
        mock_rich_text = [
            {"plain_text": "Hello ", "annotations": {"bold": False}},
            {"plain_text": "World", "annotations": {"bold": True}},
        ]
        result = format_rich_text(mock_rich_text)
        assert result == "Hello **World**"

    def test_empty(self):
        mock_rich_text = []
        result = format_rich_text(mock_rich_text)
        assert result == ""

    def test_no_annotations(self):
        mock_rich_text = [
            {"plain_text": "Just text without ", "annotations": {"bold": False}},
            {"plain_text": "formatting", "annotations": {"bold": False}},
        ]
        result = format_rich_text(mock_rich_text)
        assert result == "Just text without formatting"


class TestGetPageID:
    def test_exact_match(self):
        DUMMY_PAGE_ID = "1234abcd5678efgh"
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "id": DUMMY_PAGE_ID,
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [
                                {
                                    "plain_text": "My Test Page",
                                },
                            ],
                        }
                    },
                }
            ]
        }

        result = get_page_id(mock_client, "My Test Page")
        assert result == DUMMY_PAGE_ID
        mock_client.search.assert_called_once()

    def test_no_match(self):
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "id": "irrelevant-id",
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [
                                {
                                    "plain_text": "Another Page",
                                },
                            ],
                        }
                    },
                }
            ]
        }

        result = get_page_id(mock_client, "Nonexistent Page")
        assert result is None
        mock_client.search.assert_called_once()

    def test_ambiguous_title(self):
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "id": "id-1",
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [
                                {
                                    "plain_text": "Common Title",
                                },
                            ],
                        }
                    },
                },
                {
                    "id": "id-2",
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [
                                {
                                    "plain_text": "Common Title",
                                },
                            ],
                        }
                    },
                },
            ]
        }
        with pytest.raises(AmbiguousTitleError):
            get_page_id(mock_client, "Common Title")
        mock_client.search.assert_called_once()


class TestGetPageContent:
    def test_missing_page(self):
        mock_client = MagicMock()
        with patch("flashcards.notion.get_page_id", return_value=None):
            with pytest.raises(PageNotFoundError):
                get_page_content(mock_client, "Missing Page", count=1)

    def test_empty_blocks(self):
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
        with patch("flashcards.notion.get_page_id", return_value="dummy_id"):
            with pytest.raises(PageEmptyError):
                get_page_content(mock_client, "Page With Empty Block", count=1)

    def test_respects_count_limit(self):
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
        with patch("flashcards.notion.get_page_id", return_value="dummy_id"):
            result = get_page_content(mock_client, "Limited Page", count=2)
            assert result == ["**First**", "**Second**"]

    def test_skips_non_bolded(self):
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
        with patch("flashcards.notion.get_page_id", return_value="dummy_id"):
            result = get_page_content(mock_client, "Mixed Page", count=1)
            assert result == ["**Yes bold**"]

    def test_fewer_bolded_than_count(self):
        mock_client = MagicMock()
        mock_client.blocks.children.list.return_value = {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"plain_text": "One", "annotations": {"bold": True}}
                        ]
                    },
                }
            ]
        }
        with patch("flashcards.notion.get_page_id", return_value="dummy_id"):
            result = get_page_content(mock_client, "Short Page", count=3)
            assert result == ["**One**"]
