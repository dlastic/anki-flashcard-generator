import sys

from notion_utils import get_page_content


def main() -> None:
    """Generate anki cloze deck from sentences in the Notion page."""
    title = sys.argv[1]
    content = get_page_content(title)
    if content is None:
        sys.exit(f"Exiting: No page found with title: {title}")

    print("Page content loaded successfully.")


if __name__ == "__main__":
    main()
