import argparse
import os
import sys

from loguru import logger


def build_argument_parser() -> argparse.ArgumentParser:
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
    parser.add_argument(
        "-c",
        "--count",
        default=5,
        type=int,
        help="Maximum number of sentences to translate (default: 5)",
    )
    parser.add_argument(
        "-a",
        "--api",
        default="gemini",
        type=str.lower,
        choices=["gemini", "openai"],
        help="LLM API to use: 'gemini' or 'openai' (default: gemini)",
    )
    return parser


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

    OUTPUT_FILENAME = "flashcard_deck.apkg"
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, OUTPUT_FILENAME)

    parser = build_argument_parser()
    args = parser.parse_args()

    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    source_lang, target_lang, sentence_count, api = (
        args.source,
        args.target,
        args.count,
        args.api,
    )
    if source_lang not in LANGUAGE_CODE_MAP:
        logger.error(f"Unsupported source language: {source_lang}")
        sys.exit(1)
    if target_lang not in LANGUAGE_DECK_MAP:
        logger.error(f"Unsupported target language: {target_lang}")
        sys.exit(1)

    from .generator import (
        DeckGenerationError,
        FlashcardGenerationError,
        generate_cloze_deck,
        generate_flashcards,
    )
    from .notion_utils import PageEmptyError, PageNotFoundError, get_page_content
    from .translate_utils import TranslationError, translate_sentences

    try:
        content = get_page_content(target_lang, sentence_count)
        logger.success("Page content loaded successfully.")
    except (PageNotFoundError, PageEmptyError) as e:
        logger.error(str(e))
        sys.exit(1)

    try:
        translated_content = translate_sentences(
            sentences=content, source_lang=source_lang, api=api
        )
        logger.success("Translation completed successfully.")
    except TranslationError as e:
        logger.error(f"Translation failed: {e}")
        sys.exit(1)

    try:
        flashcards = generate_flashcards(translated_content)
        logger.success("Flashcards generated successfully.")
    except FlashcardGenerationError as e:
        logger.error(f"Flashcard generation failed: {e}")
        sys.exit(1)

    try:
        generate_cloze_deck(LANGUAGE_DECK_MAP[target_lang], flashcards, output_path)
        logger.success(f"Anki cloze deck generated successfully at: {output_path}")
    except DeckGenerationError as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
