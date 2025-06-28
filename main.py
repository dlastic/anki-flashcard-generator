import sys

from general_utils import print_seperating_line
from notion_utils import get_page_content
from translate_utils import translate_sentences_chatgpt


def main() -> None:
    """Generate anki cloze deck from sentences in the Notion page."""
    title = sys.argv[1]
    content = get_page_content(title)
    if content is None:
        print_seperating_line()
        sys.exit(f"Exiting: No page found with title: {title}")

    print_seperating_line()
    print("Page content loaded successfully.")

    translated_content = [
        ["yapping", "Why are you <u>yapping</u> at me?"],
        ["rot", "I thought you'd leave me to <u>rot</u> here."],
        ["something to eat", "Can I get <u>something to eat</u>?"],
        ["screw loose", "You have just as much of a <u>screw loose</u> as I do, man."],
        ["gasping", "Then he starts off <u>gasping</u>."],
    ]
    print_seperating_line()
    if translated_content is None:
        sys.exit("Exiting: No sentences to translate.")

    print("Translation completed successfully.")


if __name__ == "__main__":
    main()
