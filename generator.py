import re
import logging

import genanki


class FlashcardGenerationError(Exception):
    pass


class DeckGenerationError(Exception):
    pass


logger = logging.getLogger(__name__)


def convert_underline_to_cloze(sentence: str) -> str:
    """Replace <u>word</u> with {{c1::word}}"""
    return re.sub(r"<u>(.*?)</u>", r"{{c1::\1}}", sentence)


def generate_flashcards(
    content: list[str], translated_content: list[list[str]]
) -> list[str]:
    """Generate a list of flashcards"""
    content_len = len(content)
    translated_content_len = len(translated_content)
    if content_len != translated_content_len:
        raise FlashcardGenerationError(
            f"Content length ({content_len}) and translated content length ({translated_content_len}) do not match."
        )

    flashcards = []
    for target_line, translation in zip(content, translated_content):
        if not (isinstance(translation, (list, tuple)) and len(translation) == 2):
            logger.warning(
                f"Skipping flashcard due to invalid translation format: {translation}"
            )
            continue
        if "<u>" not in target_line or "</u>" not in target_line:
            logger.warning(
                f"Skipping flashcard due to missing underline tags in: {target_line}"
            )
            continue
        source_word, source_sentence = translation
        target_line_cloze = convert_underline_to_cloze(target_line)
        flashcards.append(
            f"<i>{source_word}</i><br><i>{source_sentence}</i><br>{target_line_cloze}"
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
