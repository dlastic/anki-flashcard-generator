import logging
import re

import genanki

from translate_utils import TranslationItem


class FlashcardGenerationError(Exception):
    pass


class DeckGenerationError(Exception):
    pass


logger = logging.getLogger(__name__)


def convert_underline_to_cloze(sentence: str) -> str:
    """Replace <u>word</u> with {{c1::word}}"""
    return re.sub(r"<u>(.*?)</u>", r"{{c1::\1}}", sentence)


def generate_flashcards(translated_content: list[TranslationItem]) -> list[str]:
    """Generate a list of flashcards"""
    flashcards = []
    for translation in translated_content:
        words_source, sentence_source, sentence_target = (
            translation.words_source,
            translation.sentence_source,
            translation.sentence_target,
        )

        if "<u>" not in sentence_target or "</u>" not in sentence_target:
            logger.warning(
                f"Skipping flashcard due to missing underline tags in: {sentence_target}"
            )
            continue

        sentence_target_cloze = convert_underline_to_cloze(sentence_target)
        flashcards.append(
            f"<i>{words_source}</i><br><i>{sentence_source}</i><br>{sentence_target_cloze}"
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
