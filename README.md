# Anki Flashcard Generator

This project automatically generates Anki flashcards for language learning. It fetches sentences from a Notion page, identifies a specific word to learn in each sentence, uses an AI translation service to generate a definition and a full sentence translation, fetches an image describing the word, and then creates a ready-to-import Anki deck with cloze deletion cards.

## Features

- **Notion Integration**: Directly pulls sentences from a designated Notion page.
- **AI-Powered Translation**: Utilizes Gemini or OpenAI models to provide context-aware translations for bold words and full sentences.
- **Cloze Deletion Cards**: Automatically generates flashcards where the word to be learned is hidden (cloze deletion).
- **Multi-Language Support**: Easily configurable for various source and target languages. The target language determines which Notion page to read from and which Anki deck to generate.
- **Customizable**: A command-line interface allows you to specify the source and target languages, the number of cards to generate, and the LLM API.
- **Batch Processing**: Generate multiple flashcards at once, streamlining the card creation process.

## Usage

1. Clone the repository and install the required dependencies:

```bash
git clone https://github.com/dlastic/anki-flashcard-generator.git
cd anki-flashcard-generator
uv sync
```

2. Add your API keys for Notion, Gemini, Google Custom Search, and optionally OpenAI in the `.env` file (copy `.env.example` to `.env` and update the values):

```bash
cp .env.example .env
```

3. Run the command from the project root:

```bash
uv run anki -t TARGET [options]
```

### Required Arguments

- `-t`, `--target`: The language you are learning (target language).

### Optional Arguments

- `-s`, `--source`: The language you know (source language). Defaults to `EN`.
- `-c`, `--count`: The maximum number of flashcards to generate. Defaults to `5`.
- `-a`, `--api`: LLM API to use: `gemini` or `openai` (**default**: `gemini`)
- `-m`, `--model`: LLM model to use (default: `gpt-4o` for OpenAI,
  `gemini-3-flash-preview` for Gemini)

### Example

To generate 10 flashcards for French using the OpenAI API (with English as the source language), run:

```bash
uv run anki -t FR -c 10 -a openai
```

Upon successful execution, a file named `flashcard_deck.apkg` will be created in the `output/` directory. You can then import this file directly into your Anki application.
