import os
import sys

from loguru import logger

from .cli import build_argument_parser, load_environment, setup_logger


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

    setup_logger()
    load_environment()
    parser = build_argument_parser()
    args = parser.parse_args()

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
    from .notion import (
        PageEmptyError,
        PageNotFoundError,
        get_notion_client,
        get_page_content,
    )
    from .translation import TranslationError, translate_sentences

    try:
        notion_client = get_notion_client()
    except ValueError as e:
        logger.error(f"Failed to initialize Notion client: {e}")
        sys.exit(1)

    try:
        content = get_page_content(notion_client, target_lang, sentence_count)
        logger.success("Page content loaded successfully.")
    except (PageNotFoundError, PageEmptyError) as e:
        logger.error(f"Failed to get page content: {e}")
        sys.exit(1)

    try:
        translated_content = translate_sentences(
            sentences=content,
            source_lang=source_lang,
            api=api,
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
