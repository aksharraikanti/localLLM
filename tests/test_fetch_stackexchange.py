import pytest
import requests
import time

from scripts.fetch_stackexchange import fetch_questions


def test_fetch_questions_not_implemented():
    """fetch_questions should raise NotImplementedError until implemented."""
    with pytest.raises(NotImplementedError):
        fetch_questions(
            tags=["kubernetes"],
            page_size=10,
            api_key="key",
            access_token="token",
        )


def test_fetch_questions_pagination(monkeypatch):
    """Test pagination logic of fetch_questions with mocked responses."""
    # Simulate two pages of API responses
    responses = [
        {"items": [{"id": 1}], "has_more": True},
        {"items": [{"id": 2}], "has_more": False},
    ]

    class DummyResp:
        def __init__(self, data):
            self._data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self._data

    calls = []

    def fake_get(url, params=None):
        calls.append(params.copy())
        return DummyResp(responses.pop(0))

    monkeypatch.setattr(requests, "get", fake_get)
    # avoid real sleep delays in test
    monkeypatch.setattr(time, "sleep", lambda _: None)
    result = fetch_questions(["k8s"], page_size=1, api_key="key")
    assert result == [{"id": 1}, {"id": 2}]
    # Verify pagination incremented page parameter
    assert calls[0]["page"] == 1
    assert calls[1]["page"] == 2
