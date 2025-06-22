from notion_utils import extract_page_title


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
