import pytest

from flashcards.generator import _convert_bold_text


class TestConvertBoldText:
    @pytest.mark.parametrize(
        "sentence, format_type, expected",
        [
            ("**Test** sentence.", "cloze", "{{c1::Test}} sentence."),
            ("Underline **this** word.", "underline", "Underline <u>this</u> word."),
            ("No bold here.", "cloze", "No bold here."),
            ("No bold here.", "underline", "No bold here."),
        ],
    )
    def test_valid_format(self, sentence, format_type, expected):
        assert _convert_bold_text(sentence, format_type) == expected

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            _convert_bold_text("**Test** sentence.", "invalid_format")
