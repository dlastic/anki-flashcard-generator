import re
from pathlib import Path

import genanki
from loguru import logger

from .translation import TranslationItem


class FlashcardGenerationError(Exception):
    pass


class DeckGenerationError(Exception):
    pass


BOLD_PATTERN = re.compile(r"\*\*(.*?)\*\*")
FORMAT_PATTERNS = {
    "cloze": r"{{c1::\1}}",
    "underline": r"<u>\1</u>",
}
DECK_ID = 2025051101


def _convert_bold_text(sentence: str, format_type: str) -> str:
    """Replace **word** with {{c1::word}} or <u>word</u> based on format_type."""
    if format_type not in FORMAT_PATTERNS:
        raise ValueError(f"Unsupported format type: {format_type}")
    return BOLD_PATTERN.sub(FORMAT_PATTERNS[format_type], sentence)


def _format_flashcard(words: str, source: str, target: str) -> str:
    """Format a flashcard with underlined source and cloze target."""
    return (
        f"<i>{words}</i><br>"
        f"<i>{_convert_bold_text(source, 'underline')}</i><br>"
        f"{_convert_bold_text(target, 'cloze')}"
    )


def generate_flashcards(translated_content: list[TranslationItem]) -> list[str]:
    """Generate a list of flashcards"""
    flashcards = []
    for translation in translated_content:
        words, sentence_source, sentence_target = (
            translation.words_source,
            translation.sentence_source,
            translation.sentence_target,
        )

        if "**" not in sentence_target:
            logger.warning(f"Skipping flashcard due to missing bold tags in: {sentence_target}")  # fmt:skip
            continue

        flashcards.append(_format_flashcard(words, sentence_source, sentence_target))

    return flashcards


def generate_cloze_deck(
    deck_name: str,
    flashcards: list[str],
    output_path: str | Path,
) -> None:
    """Generate a file with a deck of anki cloze cards."""
    deck = genanki.Deck(DECK_ID, deck_name)

    for flashcard in flashcards:
        if not isinstance(flashcard, str) or not flashcard.strip():
            logger.warning(f"Skipping flashcard due to invalid content: {flashcard}")
            continue
        deck.add_note(genanki.Note(model=genanki.CLOZE_MODEL, fields=[flashcard, ""]))

    try:
        genanki.Package(deck).write_to_file(output_path)
    except Exception as e:
        raise DeckGenerationError(f"Failed to write deck: {e}") from e
