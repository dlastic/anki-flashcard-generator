import logging
import os
from typing import cast

from dotenv import load_dotenv
from notion_client import Client


class PageNotFoundError(Exception):
    pass


class PageEmptyError(Exception):
    pass


logger = logging.getLogger(__name__)
load_dotenv()
notion = Client(auth=os.getenv("NOTION_API_KEY"))


def extract_page_title(result: dict) -> str | None:
    """Extract the plain-text title from a Notion page object."""
    properties = result.get("properties", {})

    for prop in properties.values():
        if prop.get("type") == "title":
            return prop["title"][0]["plain_text"]

    return None


def get_page_id(title: str) -> str | None:
    """Search for a page by title using Notion API."""
    response = cast(
        dict,
        notion.search(
            query=title,
            sort={"direction": "ascending", "timestamp": "last_edited_time"},
            filter={"value": "page", "property": "object"},
        ),
    )

    for result in response["results"]:
        result_title = extract_page_title(result)
        if title == result_title:
            return result["id"]

    return None


def format_rich_text(rich_text_array: list[dict]) -> str:
    """Convert Notion rich_text fragments to Markdown-style formatted text."""
    parts = []

    for fragment in rich_text_array:
        text = fragment.get("plain_text", "")
        anno = fragment.get("annotations", {})

        if anno.get("bold"):
            text = f"**{text}**"

        parts.append(text)

    return "".join(parts)


def get_page_content(title: str, count: int) -> list[str]:
    """Return plain text content lines of a Notion page by its title."""
    page_id = get_page_id(title)
    if not page_id:
        raise PageNotFoundError(f"No Notion page found with title: {title}")

    response = cast(dict, notion.blocks.children.list(block_id=page_id))

    content_lines = []
    for block in response.get("results", []):
        block_type = block.get("type")
        text_items = block.get(block_type, {}).get("rich_text", [])
        block_text = format_rich_text(text_items)

        if block_text:
            if "**" not in block_text:
                logger.warning(f"No **bold** word found: {block_text}")
                continue
            content_lines.append(block_text)
            if len(content_lines) == count:
                break

    if not content_lines:
        raise PageEmptyError(
            f"Page '{title}' contains no usable content with **bold** text."
        )

    return content_lines
