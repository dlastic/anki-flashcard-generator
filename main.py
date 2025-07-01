import json
import sys

from generator import generate_cloze_deck, generate_flashcards
from notion_utils import get_page_content
from translate_utils import translate_sentences_chatgpt


def main() -> None:
    """Generate anki cloze deck from sentences in the Notion page."""
    output_path = "./output/output.apkg"
    title = sys.argv[1]
    content = get_page_content(title)
    print_seperating_line()
    if content is None:
        sys.exit(f"Exiting: No page found with title: {title}")
    print("Page content loaded successfully.")

    translated_content = translate_sentences_chatgpt(content)
    print_seperating_line()
    if translated_content is None:
        sys.exit("Exiting: No sentences to translate.")
    print("Translation completed successfully.")

    flashcards = generate_flashcards(content, json.loads(translated_content))
    print_seperating_line()
    print("Flashcards generated successfully.")

    generate_cloze_deck(title, flashcards, output_path)
    print_seperating_line()
    print(f"Anki cloze deck generated successfully at: {output_path}")


def print_seperating_line() -> None:
    print("--------------------------------------------")


if __name__ == "__main__":
    main()
