import pytest

from flashcards.notion_utils import (
    PageEmptyError,
    get_notion_client,
    get_page_content,
    get_page_id,
)


@pytest.fixture(scope="module")
def notion_client():
    return get_notion_client()


class TestNotionGetPageID:
    def test_notion_page_id(self, notion_client):
        page_id = "2e275c51-aa1d-80c1-b508-ffea172c880d"
        assert get_page_id(notion_client, "test_page_non_empty") == page_id


class TestNotionGetPageContent:
    def test_notion_empty_page(self, notion_client):
        with pytest.raises(PageEmptyError):
            get_page_content(notion_client, "test_page_empty")

    def test_notion_non_empty_page(self, notion_client):
        content = get_page_content(notion_client, "test_page_non_empty")
        assert len(content) > 0
