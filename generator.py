import re

import genanki
from loguru import logger

from translate_utils import TranslationItem


class FlashcardGenerationError(Exception):
    pass


class DeckGenerationError(Exception):
    pass


def convert_bold_text(sentence: str, format_type: str) -> str:
    """Replace **word** with {{c1::word}} or <u>word</u> based on format_type."""
    pattern = r"\*\*(.*?)\*\*"
    if format_type == "cloze":
        replacement = r"{{c1::\1}}"
    elif format_type == "underline":
        replacement = r"<u>\1</u>"
    else:
        raise ValueError(f"Unsupported format type: {format_type}")

    return re.sub(pattern, replacement, sentence)


def generate_flashcards(translated_content: list[TranslationItem]) -> list[str]:
    """Generate a list of flashcards"""
    flashcards = []
    for translation in translated_content:
        words_source, sentence_source, sentence_target = (
            translation.words_source,
            translation.sentence_source,
            translation.sentence_target,
        )

        if "**" not in sentence_target:
            logger.warning(
                f"Skipping flashcard due to missing bold tags in: {sentence_target}"
            )
            continue

        sentence_source_underline = convert_bold_text(sentence_source, "underline")
        sentence_target_cloze = convert_bold_text(sentence_target, "cloze")
        flashcards.append(
            f"<i>{words_source}</i><br><i>{sentence_source_underline}</i><br>{sentence_target_cloze}"
        )

    return flashcards


def generate_cloze_deck(
    deck_name: str, flashcards: list[str], output_path: str
) -> None:
    """Generate a file with a deck of anki cloze cards."""
    deck = genanki.Deck(2025051101, deck_name)

    for flashcard in flashcards:
        if not isinstance(flashcard, str) or not flashcard.strip():
            logger.warning(f"Skipping flashcard due to invalid content: {flashcard}")
            continue
        note = genanki.Note(model=genanki.CLOZE_MODEL, fields=[flashcard, ""])
        deck.add_note(note)

    try:
        genanki.Package(deck).write_to_file(output_path)
    except Exception as e:
        raise DeckGenerationError(f"Failed to write deck: {e}") from e
