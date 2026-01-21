from unittest.mock import Mock, patch

import pytest

from flashcards.images import _get_credentials, _search_images


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
