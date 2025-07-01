import re

import genanki


def convert_underline_to_cloze(sentence: str) -> str:
    """Replace <u>word</u> with {{c1::word}}"""
    return re.sub(r"<u>(.*?)</u>", r"{{c1::\1}}", sentence)


def generate_flashcards(
    content: list[str], translated_content: list[list[str]]
) -> list[str]:
    """Generate a list of flashcards"""
    flashcards = []
    for target_line, translation in zip(content, translated_content):
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
        text_field = flashcard
        note = genanki.Note(model=genanki.CLOZE_MODEL, fields=[text_field, ""])
        deck.add_note(note)

    genanki.Package(deck).write_to_file(output_path)
