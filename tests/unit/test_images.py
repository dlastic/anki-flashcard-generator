from io import BytesIO
from unittest.mock import Mock, patch

import pytest
import requests
from PIL import Image

from flashcards.images import (
    _fetch_images,
    _get_credentials,
    _resize_image,
    _search_images,
)


@pytest.fixture
def jpeg_bytes():
    buf = BytesIO()
    Image.new("RGB", (1, 1)).save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def img():
    return Image.new("RGB", (200, 100))


class TestGetCredentials:
    def test_success(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_API_KEY", "key")
        monkeypatch.setenv("SEARCH_ENGINE_ID", "cx")

        api_key, eng_id = _get_credentials()
        assert api_key == "key"
        assert eng_id == "cx"

    def test_raises_on_missing(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("SEARCH_ENGINE_ID", raising=False)

        with pytest.raises(RuntimeError):
            _get_credentials()


class TestSearchImages:
    def test_invalid_num_raises(self):
        with pytest.raises(ValueError):
            _search_images("key", "cx", "q", num=0)

    def test_success_returns_links(self):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "items": [
                {"link": "http://a.com/1.jpg"},
                {"link": "http://b.com/2.jpg"},
                {"link": None},
            ]
        }

        with patch("flashcards.images.requests.get", return_value=mock_resp):
            links = _search_images("key", "cx", "q", num=3)

        assert links == ["http://a.com/1.jpg", "http://b.com/2.jpg"]

    def test_http_error_raises_runtime(self):
        mock_resp = Mock()
        mock_resp.status_code = 403
        mock_resp.json.return_value = {"error": {"message": "Quota exceeded"}}
        mock_resp.text = "Forbidden"

        with patch("flashcards.images.requests.get", return_value=mock_resp):
            with pytest.raises(RuntimeError) as exc:
                _search_images("key", "cx", "q")

        assert "Quota exceeded" in str(exc.value)


class TestFetchImages:
    def test_returns_images_and_respects_n(self, jpeg_bytes):
        resp = Mock()
        resp.raise_for_status.return_value = None
        resp.content = jpeg_bytes
        with patch("flashcards.images.requests.Session.get", return_value=resp):
            assert len(_fetch_images(["u1", "u2"], n=1)) == 1

    def test_errors_are_skipped(self):
        with patch("flashcards.images.requests.Session.get") as mock_get:
            mock_get.side_effect = requests.RequestException("fail")
            images = _fetch_images(["u1"], n=1)
        assert len(images) == 0

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            _fetch_images(["u1"], n=0)


class TestResizeImage:
    @pytest.mark.parametrize(
        "box, expected",
        [
            ((100, 100), (100, 50)),
            ((300, 300), (200, 100)),
            ((50, 50), (50, 25)),
            ((200, 100), (200, 100)),
        ],
    )
    def test_resize_image(self, img, box, expected):
        resized = _resize_image(img, box)
        assert resized.size == expected

    def test_original_image_not_modified(self, img):
        original_size = img.size
        _resize_image(img, (100, 100))
        assert img.size == original_size
