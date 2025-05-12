from generator import generate_cloze_deck


def main():
    deck_name = "Generated Deck"
    output_path = "./output/output.apkg"

    flashcards = [
        ("I go to school every day.", "Chodím do {{c1::školy}} každý den."),
        ("She is a good friend.", "Je to {{c1::dobrá}} kamarádka."),
    ]

    generate_cloze_deck(deck_name, flashcards, output_path)
    print(f"Deck '{deck_name}' has been generated and saved to '{output_path}'.")


if __name__ == "__main__":
    main()
