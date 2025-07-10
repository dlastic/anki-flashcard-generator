import argparse
import json
import sys

from generator import generate_cloze_deck, generate_flashcards
from notion_utils import get_page_content
from translate_utils import translate_sentences_chatgpt


def main() -> None:
    """Generate anki cloze deck from sentences in the Notion page."""
    LANGUAGE_DECK_MAP = {
        "EN": "01_Languages::01_English",
        "FR": "01_Languages::02_Français",
        "RU": "01_Languages::03_Русский",
        "DE": "01_Languages::04_Deutsch",
        "IT": "01_Languages::05_Italiano",
        "FA": "01_Languages::06_Farsi",
        "ES": "01_Languages::07_Español",
    }

    LANGUAGE_CODE_MAP = {
        "EN": "English",
        "SK": "Slovak",
    }

    parser = argparse.ArgumentParser(description="Language description")
    parser.add_argument(
        "-s",
        "--source",
        default="EN",
        type=str.upper,
        help="Source language (default: EN)",
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        type=str.upper,
        help="Target language (required)",
    )
    args = parser.parse_args()

    output_path = "./output/output.apkg"
    source_lang, target_lang = args.source, args.target

    if source_lang not in LANGUAGE_CODE_MAP:
        sys.exit(f"Exiting: Unsupported source language: {source_lang}")
    if target_lang not in LANGUAGE_DECK_MAP:
        sys.exit(f"Exiting: Unsupported target language: {target_lang}")

    content = get_page_content(target_lang)
    print_seperating_line()
    if content is None:
        sys.exit(f"Exiting: No page found with title: {target_lang}")
    print("Page content loaded successfully.")

    translated_content = translate_sentences_chatgpt(content, source_lang)
    print_seperating_line()
    if translated_content is None:
        sys.exit("Exiting: No sentences to translate.")
    print("Translation completed successfully.")

    flashcards = generate_flashcards(content, json.loads(translated_content))
    print_seperating_line()
    print("Flashcards generated successfully.")

    generate_cloze_deck(LANGUAGE_DECK_MAP[target_lang], flashcards, output_path)
    print_seperating_line()
    print(f"Anki cloze deck generated successfully at: {output_path}")


def print_seperating_line() -> None:
    print("--------------------------------------------")


if __name__ == "__main__":
    main()
