import os

import pytest
from PIL import Image

from flashcards.images import get_multiple_image_sets

REQUIRED_API_KEYS = ["GOOGLE_API_KEY", "SEARCH_ENGINE_ID"]


@pytest.fixture(scope="session", autouse=True)
def check_api_keys():
    missing = [key for key in REQUIRED_API_KEYS if os.getenv(key) is None]
    if missing:
        pytest.exit(f"Missing required API keys: {', '.join(missing)}")


class TestGetMultipleImageSets:
    def test_success(self, tmp_path):
        queries = ["cat", "dog"]
        img_file_paths, img_tags_list = get_multiple_image_sets(
            queries,
            tmp_path,
            5,
            (400, 200),
        )

        assert len(img_file_paths) == 10
        assert len(img_tags_list) == 2

        for p in img_file_paths:
            img = Image.open(p)
            assert img.size[0] <= 400
            assert img.size[1] <= 200
