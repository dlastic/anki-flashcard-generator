# Anki Flashcard Generator

This project automatically generates Anki flashcards for language learning. It fetches sentences from a Notion page, identifies a specific word to learn in each sentence, uses an AI translation service to get its definition and a full sentence translation, and then creates a ready-to-import Anki deck with cloze deletion cards.

## Features

- **Notion Integration**: Directly pulls sentences from a designated Notion page.
- **AI-Powered Translation**: Utilizes Google Gemini or OpenAI GPT to provide context-aware translations for underlined words and full sentences.
- **Cloze Deletion Cards**: Automatically generates flashcards where the word to be learned is hidden (cloze deletion).
- **Multi-Language Support**: Easily configurable for various source and target languages. The target language determines which Notion page to read from and which Anki deck to generate.
- **Customizable**: A command-line interface allows you to specify the source and target languages and the number of cards to generate.
- **Batch Processing**: Generate multiple flashcards at once, streamlining the card creation process.

## Workflow

1.  **Fetch Content**: The script connects to your Notion workspace using the API and finds the page corresponding to your target language (e.g., a page titled "FR" for French).
2.  **Parse Sentences**: It reads the content of the page, looking for text blocks. It specifically processes lines that contain an `<u>underlined</u>` word, which is the word you intend to learn.
3.  **Translate**: Each sentence with an underlined word is sent to the Google Gemini API / OpenAI API. The script prompts the AI to provide two translations for the underlined word and a full translation of the sentence.
4.  **Generate Flashcards**: The original sentence and the AI-generated translations are formatted into Anki flashcards. The card format is:
    - The translated (source language) word, the translated sentence, and the original (target language) sentence with the underlined word hidden in a cloze deletion.
5.  **Create Anki Deck**: The generated flashcards are packaged into an `.apkg` file, which can be directly imported into Anki.

## Usage

Run the `main.py` script from your terminal, specifying the target language.

### Arguments

- `-s`, `--source`: The language you know (for the translation). Defaults to `EN`.
- `-t`, `--target`: The language you are learning. This is **required** and must match a Notion page title.
- `-c`, `--count`: The maximum number of flashcards to generate. Defaults to `5`.

### Example

To generate 10 flashcards for French, assuming your source language is English, run:

```bash
python main.py -t FR -c 10
```

Upon successful execution, a file named `flashcard_deck.apkg` will be created in the `output/` directory. You can then import this file directly into your Anki application.
