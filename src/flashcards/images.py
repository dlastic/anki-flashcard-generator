import os
import uuid
from io import BytesIO
from pathlib import Path

import requests
from loguru import logger
from PIL import Image


def _get_credentials() -> tuple[str, str]:
    """Retrieve Google Custom Search API credentials from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY")
    eng_id = os.getenv("SEARCH_ENGINE_ID")

    if api_key is None or eng_id is None:
        raise RuntimeError(
            "Missing Google Custom Search credentials. "
            "Set GOOGLE_API_KEY and SEARCH_ENGINE_ID environment variables."
        )

    return api_key, eng_id


def _search_images(api_key: str, eng_id: str, query: str, num: int = 10) -> list[str]:
    """Return list of image URLs from Google Custom Search."""
    if num <= 0:
        raise ValueError("num must be > 0")

    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": eng_id,
        "q": query,
        "searchType": "image",
        "num": min(num, 10),
    }
    resp = requests.get(base_url, params=params, timeout=1)
    if resp.status_code != 200:
        try:
            err = resp.json().get("error", {}).get("message")
        except Exception:
            err = resp.text
        raise RuntimeError(f"Google Custom Search failed ({resp.status_code}): {err}")

    data = resp.json()
    items = data.get("items", [])
    return [item.get("link") for item in items if item.get("link")]


def _fetch_images(
    urls: list[str],
    n: int,
    timeout: int = 1,
) -> list[Image.Image]:
    """Download images into memory and return PIL Image objects."""
    if n <= 0:
        raise ValueError("n must be > 0")

    session = requests.Session()
    images: list[Image.Image] = []
    for url in urls:
        if len(images) >= n:
            break
        try:
            resp = session.get(url, timeout=timeout)
            resp.raise_for_status()
            with Image.open(BytesIO(resp.content)) as img:
                images.append(img.convert("RGB"))
        except (requests.RequestException, OSError) as e:
            logger.debug(f"Failed to fetch image {url}: {e}")
            continue
    return images


def _resize_image(
    img: Image.Image,
    box: tuple[int, int],
) -> Image.Image:
    """Return a resized copy of the image fitting within box."""
    resized = img.copy()
    resized.thumbnail(box)
    return resized


def _save_image(img: Image.Image, out_path: Path, quality: int = 85) -> Path:
    """Save a PIL image to disk and return the path."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if img.mode != "RGB":
        img = img.convert("RGB")

    img.save(out_path, format="JPEG", quality=quality)
    return out_path


def _generate_filename_from_query(query: str, ext: str = ".jpg") -> str:
    """Generate a unique filename based on the query."""
    name = query.split(",")[0]
    uid = uuid.uuid4().hex
    return f"{name}-{uid}{ext}"


def get_multiple_image_sets(
    queries: list[str],
    out_dir: Path,
    imgs_per_query: int = 5,
    box: tuple[int, int] = (400, 200),
) -> tuple[list[Path], list[str]]:
    """Fetch, resize, and save images for multiple queries."""
    api_key, cx = _get_credentials()

    img_file_paths: list[Path] = []
    img_tags_list = []

    for query in queries:
        urls = _search_images(api_key, cx, query)
        images = _fetch_images(urls, n=imgs_per_query)
        img_tags = []
        for img in images:
            resized = _resize_image(img, box)
            filename = _generate_filename_from_query(query, ext=".jpg")
            out_path = out_dir / filename
            img_file_paths.append(_save_image(resized, out_path))
            img_tags.append(f"<img src='{filename}'>")
        img_tags_list.append("".join(img_tags))

    return img_file_paths, img_tags_list


def delete_files(files: list[Path]) -> None:
    """Delete files from disk."""
    for file in files:
        if file.exists():
            file.unlink()
