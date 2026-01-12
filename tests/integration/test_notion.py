import pytest

from flashcards.notion import (
    AmbiguousTitleError,
    PageEmptyError,
    PageNotFoundError,
    get_notion_client,
    get_page_content,
    get_page_id,
)


@pytest.fixture(scope="module")
def notion_client():
    return get_notion_client()


class TestGetPageID:
    def test_success(self, notion_client):
        page_id = "2e275c51-aa1d-80c1-b508-ffea172c880d"
        assert get_page_id(notion_client, "test_page_non_empty") == page_id

    def test_ambiguous_title(self, notion_client):
        with pytest.raises(AmbiguousTitleError):
            get_page_id(notion_client, "Common Title")

    def test_missing_page(self, notion_client):
        assert get_page_id(notion_client, "Nonexistent Page") is None


class TestGetPageContent:
    def test_empty_page(self, notion_client):
        with pytest.raises(PageEmptyError):
            get_page_content(notion_client, "test_page_empty")

    def test_non_empty_page(self, notion_client):
        content = get_page_content(notion_client, "test_page_non_empty")
        assert len(content) > 0

    def test_missing_page(self, notion_client):
        with pytest.raises(PageNotFoundError):
            get_page_content(notion_client, "Nonexistent Page")
