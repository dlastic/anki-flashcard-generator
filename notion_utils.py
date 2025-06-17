from bs4 import BeautifulSoup, Tag


def extract_paragraph_texts(filepath: str) -> list[str]:
    """Extract and return all paragraph texts inside the page-body div."""
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    page_body = soup.find("div", class_="page-body")
    if not isinstance(page_body, Tag):
        return []

    return [p.get_text(strip=True) for p in page_body.find_all("p")]


sample_filepath = "./input/input.html"
output = extract_paragraph_texts(sample_filepath)
for sentence in output:
    print(sentence)
