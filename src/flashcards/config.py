from pathlib import Path

LANGUAGE_DECK_MAP = {
    "EN": "01_Languages::01_English",
    "FR": "01_Languages::02_Français",
    "RU": "01_Languages::03_Русский",
    "DE": "01_Languages::04_Deutsch",
    "IT": "01_Languages::05_Italiano",
    "FA": "01_Languages::06_Farsi",
    "ES": "01_Languages::07_Español",
    "AR": "01_Languages::08_Arabic",
    "HE": "01_Languages::09_Hebrew",
}
LANGUAGE_CODE_MAP = {
    "EN": "English",
    "SK": "Slovak",
}
RTL_LANGUAGES = ("FA", "AR", "HE")

OUTPUT_FILENAME = "flashcard_deck.apkg"
OUTPUT_DIR = Path.cwd() / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / OUTPUT_FILENAME

IMAGE_TARGET_BOX = (400, 180)
