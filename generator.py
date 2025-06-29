import genanki


def generate_flashcards(
    content: list[str], translated_content: list[list[str]]
) -> list[str]:
    """Generate a list of flashcards"""
    flashcards = []
    for target_line, translation in zip(content, translated_content):
        source_word, source_sentence = translation
        flashcards.append(
            f"<i>{source_word}</i><br><i>{source_sentence}</i><br>{target_line}"
        )

    return flashcards


def generate_cloze_deck(
    deck_name: str, flashcards: list[tuple[str, str]], output_path: str
) -> None:
    """Generate a file with a deck of anki cloze cards."""
    deck = genanki.Deck(2025051101, deck_name)

    for source_line, target_line in flashcards:
        text_field = f"<i>{source_line}</i><br>{target_line}"
        note = genanki.Note(model=genanki.CLOZE_MODEL, fields=[text_field, ""])

        deck.add_note(note)

    genanki.Package(deck).write_to_file(output_path)
