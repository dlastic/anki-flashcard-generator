import argparse
import json
import logging
import sys

from generator import generate_cloze_deck, generate_flashcards
from notion_utils import get_page_content
from translate_utils import translate_sentences_chatgpt


def main() -> None:
    """Generate anki cloze deck from sentences in the Notion page."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    logger = logging.getLogger()

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
        logger.error(f"Unsupported source language: {source_lang}")
        sys.exit(1)
    if target_lang not in LANGUAGE_DECK_MAP:
        logger.error(f"Unsupported target language: {target_lang}")
        sys.exit(1)

    content = get_page_content(target_lang)
    if content is None:
        logger.error(f"No page found with title: {target_lang}")
        sys.exit(1)
    logger.info("Page content loaded successfully.")

    translated_content = translate_sentences_chatgpt(content, source_lang)
    if translated_content is None:
        logger.error("No sentences to translate.")
        sys.exit(1)
    logger.info("Translation completed successfully.")

    flashcards = generate_flashcards(content, json.loads(translated_content))
    logger.info("Flashcards generated successfully.")

    generate_cloze_deck(LANGUAGE_DECK_MAP[target_lang], flashcards, output_path)
    logger.info(f"Anki cloze deck generated successfully at: {output_path}")


if __name__ == "__main__":
    main()
