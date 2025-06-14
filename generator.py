import genanki


def generate_cloze_deck(
    deck_name: str, flashcards: list[tuple[str, str]], output_path: str
) -> None:
    deck = genanki.Deck(2025051101, deck_name)

    for source_line, target_line in flashcards:
        text_field = f"<i>{source_line}</i><br>{target_line}"
        note = genanki.Note(model=genanki.CLOZE_MODEL, fields=[text_field, ""])

        deck.add_note(note)

    genanki.Package(deck).write_to_file(output_path)
