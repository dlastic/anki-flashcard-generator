import sys

from loguru import logger

from .cli import build_argument_parser, load_environment, setup_logger
from .config import LANGUAGE_CODE_MAP, LANGUAGE_DECK_MAP, OUTPUT_PATH


def main() -> None:
    """Generate anki cloze deck from sentences in the Notion page."""
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
        generate_cloze_deck(LANGUAGE_DECK_MAP[target_lang], flashcards, OUTPUT_PATH)
        logger.success(f"Anki cloze deck generated successfully at: {OUTPUT_PATH}")
    except DeckGenerationError as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
