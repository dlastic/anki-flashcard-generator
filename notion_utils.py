import os

from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
notion = Client(auth=os.getenv("NOTION_API_KEY"))


def extract_paragraph_texts(filepath: str) -> list[str]:
    """Extract and return all paragraph texts inside the page-body div."""
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    page_body = soup.find("div", class_="page-body")
    if not isinstance(page_body, Tag):
        return []

    return [p.get_text(strip=True) for p in page_body.find_all("p")]


# def get_page_content(page_id):

#     cursor = None
#     blocks = []
#     page_id = "277f14e5-25a6-4396-ab0e-c3fc8cfb6bad"

#     while True:
#         response = notion.blocks.children.list(block_id=page_id, start_cursor=cursor)
#         blocks.extend(response["results"])
#         if not response.get("has_more"):
#             break
#         cursor = response["next_cursor"]

#     print(blocks)


def get_page_id(title: str) -> str | None:
    """Search for a page by title using Notion API."""
    if not isinstance(title, str):
        raise TypeError(f"Title must be a string, got {type(title).__name__}")

    response = notion.search(
        query=title,
        sort={"direction": "ascending", "timestamp": "last_edited_time"},
        filter={"value": "page", "property": "object"},
    )

    for result in response["results"]:
        result_title = extract_page_title(result)
        if title == result_title:
            return result["id"]

    return None


def extract_page_title(result: dict) -> str | None:
    """Extract the plain-text title from a Notion page object."""
    properties = result.get("properties", {})

    for prop in properties.values():
        if prop.get("type") == "title":
            return prop["title"][0]["plain_text"]

    return None
