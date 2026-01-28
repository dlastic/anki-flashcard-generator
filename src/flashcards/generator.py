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

# Conditionally display source words, sentence and images if the fields are not empty
FRONT_TEMPLATE = """\
{{#source_words}}<div>{{source_words}}</div>{{/source_words}}
{{#source_sentence}}<div>{{source_sentence}}</div>{{/source_sentence}}
<div class="target">{{cloze:target_sentence}}</div><br>
{{#image}}<div>{{image}}</div><br>{{/image}}
"""
BACK_TEMPLATE = FRONT_TEMPLATE + "{{Back Extra}}"
CSS_LTR = """\
.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}

.cloze {
  font-weight: bold;
  color: blue;
}

.nightMode .cloze {
  color: lightblue;
}
"""
CSS_RTL = CSS_LTR + """
.target {
  direction: rtl;
}
"""

CLOZE_MODEL_LTR = genanki.Model(
    1318636823,
    "Cloze LTR language",
    model_type=genanki.Model.CLOZE,
    fields=[
        {"name": "source_words"},
        {"name": "source_sentence"},
        {"name": "target_sentence"},
        {"name": "image"},
        {"name": "Back Extra"},
    ],
    templates=[
        {
            "name": "Cloze",
            "qfmt": FRONT_TEMPLATE,
            "afmt": BACK_TEMPLATE,
        },
    ],
    css=CSS_LTR,
)

CLOZE_MODEL_RTL = genanki.Model(
    1318636824,
    "Cloze RTL language",
    model_type=genanki.Model.CLOZE,
    fields=[
        {"name": "source_words"},
        {"name": "source_sentence"},
        {"name": "target_sentence", "rtl": True},
        {"name": "image"},
        {"name": "Back Extra"},
    ],
    templates=[
        {
            "name": "Cloze",
            "qfmt": FRONT_TEMPLATE,
            "afmt": BACK_TEMPLATE,
        },
    ],
    css=CSS_RTL,
)

def _convert_bold_text(sentence: str, format_type: str) -> str:
    """Replace **word** with {{c1::word}} or <u>word</u> based on format_type."""
    if format_type not in FORMAT_PATTERNS:
        raise ValueError(f"Unsupported format type: {format_type}")
    return BOLD_PATTERN.sub(FORMAT_PATTERNS[format_type], sentence)


def generate_cloze_deck(
    deck_name: str,
    translated_content: list[TranslationItem],
    output_path: str | Path,
    img_files: list[Path] | None,
    img_tags_list: list[str] | None,
    is_rtl: bool = False,
) -> None:
    """Generate a file with a deck of anki cloze cards."""
    deck = genanki.Deck(DECK_ID, deck_name)
    img_tags_iter = img_tags_list or [None] * len(translated_content)

    for translation, img_tags in zip(translated_content, img_tags_iter):
        if not isinstance(translation, TranslationItem):
            logger.warning(f"Skipping translation due to invalid content: {translation}")  # fmt:skip
            continue
        note = genanki.Note(
            model=CLOZE_MODEL_RTL if is_rtl else CLOZE_MODEL_LTR,
            fields=[
                f"<i>{translation.words_source}</i>",
                f"<i>{_convert_bold_text(translation.sentence_source, 'underline')}</i>",
                f"{_convert_bold_text(translation.sentence_target, 'cloze')}",
                img_tags or "",
                "",
            ],
        )
        deck.add_note(note)

    try:
        genanki.Package(deck, media_files=img_files).write_to_file(output_path)
    except Exception as e:
        raise DeckGenerationError(f"Failed to write deck: {e}") from e
