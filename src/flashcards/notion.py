import os

from dotenv import load_dotenv
from loguru import logger
from notion_client import Client


class PageNotFoundError(Exception):
    pass


class PageEmptyError(Exception):
    pass


class AmbiguousTitleError(Exception):
    pass


load_dotenv()


def get_notion_client() -> Client:
    """Initialize and return a Notion API client."""
    api_key = os.getenv("NOTION_API_KEY")
    if api_key is None:
        raise ValueError("NOTION_API_KEY environment variable is not set.")
    return Client(auth=api_key)


def extract_page_title(result: dict) -> str | None:
    """Extract the plain-text title from a Notion page object."""
    properties = result.get("properties", {})
    for prop in properties.values():
        if prop.get("type") == "title":
            return prop["title"][0]["plain_text"]
    return None


def format_rich_text(rich_text_array: list[dict]) -> str:
    """Convert Notion rich_text fragments to Markdown-style bold formatted text."""
    parts = []
    for fragment in rich_text_array:
        text = fragment.get("plain_text", "")
        anno = fragment.get("annotations", {})
        if anno.get("bold"):
            text = f"**{text}**"
        parts.append(text)
    return "".join(parts)


def get_page_id(notion_client: Client, title: str) -> str | None:
    """Search for a page by title using Notion API."""
    response = notion_client.search(
        query=title,
        filter={"value": "page", "property": "object"},
    )

    matching_results = []
    for result in response["results"]:  # ty:ignore[not-subscriptable]
        result_title = extract_page_title(result)
        if title == result_title:
            matching_results.append(result["id"])

    if len(matching_results) > 1:
        raise AmbiguousTitleError(
            f"Multiple Notion pages found with title: {title}. Please ensure titles are unique."
        )

    return matching_results[0] if matching_results else None


def get_page_content(notion_client: Client, title: str, count: int = 5) -> list[str]:
    """Return plain text content lines of a Notion page by its title."""
    page_id = get_page_id(notion_client, title)
    if not page_id:
        raise PageNotFoundError(f"No Notion page found with title: {title}")

    response = notion_client.blocks.children.list(block_id=page_id)
    content_lines = []
    for block in response.get("results", []):  # ty:ignore[possibly-missing-attribute]
        block_type = block.get("type")
        text_items = block.get(block_type, {}).get("rich_text", [])
        block_text = format_rich_text(text_items)

        if block_text:
            if "**" not in block_text:
                logger.warning(f"Skipping sentence without **bold** text: {block_text}")
                continue
            content_lines.append(block_text)
            if len(content_lines) == count:
                break

    if not content_lines:
        raise PageEmptyError(
            f"Page '{title}' contains no usable content with **bold** text."
        )

    return content_lines
