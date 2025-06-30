import json
import sys

from general_utils import print_seperating_line
from generator import generate_flashcards
from notion_utils import get_page_content
from translate_utils import translate_sentences_chatgpt


def main() -> None:
    """Generate anki cloze deck from sentences in the Notion page."""
    title = sys.argv[1]
    content = get_page_content(title)
    if content is None:
        print_seperating_line()
        sys.exit(f"Exiting: No page found with title: {title}")
    print_seperating_line()
    print("Page content loaded successfully.")

    translated_content = translate_sentences_chatgpt(content)
    print_seperating_line()
    if translated_content is None:
        sys.exit("Exiting: No sentences to translate.")
    print("Translation completed successfully.")

    flashcards = generate_flashcards(content, json.loads(translated_content))
    print_seperating_line()
    print("Flashcards generated successfully.")


if __name__ == "__main__":
    main()
