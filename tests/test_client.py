import json
import os

import pytest


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    # set API key for requests
    monkeypatch.setenv("API_KEY", "testkey")


def test_client_single_request(monkeypatch, tmp_path, capsys):
    # stub requests.post
    import localllm_client.client as client_mod

    class DummyResponse:
        def __init__(self):
            self._json = {"answer": "dummy"}

        def raise_for_status(self):
            pass

        def json(self):
            return self._json

    def dummy_post(url, json, headers):
        assert headers.get("X-API-Key") == "testkey"
        assert "/predict" in url
        assert json["question"] == "Hello"
        return DummyResponse()

    monkeypatch.setattr("requests.post", dummy_post)

    # run client
    monkeypatch.setenv("API_KEY", "testkey")
    monkeypatch.setattr(os, "environ", os.environ)
    import sys

    sys.argv = [
        "client.py",
        "--url",
        "http://test",
        "--question",
        "Hello",
        "--max-length",
        "128",
    ]
    import localllm_client.client as client

    client.main()
    captured = capsys.readouterr()
    assert '"answer": "dummy"' in captured.out


def test_client_batch_request(monkeypatch, tmp_path, capsys):
    import localllm_client.client as client_mod

    batch_file = tmp_path / "batch.json"
    batch_file.write_text(json.dumps({"questions": ["Q1", "Q2"]}), encoding="utf8")

    class DummyResponse:
        def __init__(self):
            self._json = {"answers": ["a1", "a2"]}

        def raise_for_status(self):
            pass

        def json(self):
            return self._json

    def dummy_post(url, json, headers):
        assert "/predict_batch" in url
        assert json["questions"] == ["Q1", "Q2"]
        return DummyResponse()

    monkeypatch.setattr("requests.post", dummy_post)
    import sys

    monkeypatch.setenv("API_KEY", "testkey")
    sys.argv = [
        "client.py",
        "--url",
        "http://test",
        "--batch-file",
        str(batch_file),
    ]
    import localllm_client.client as client

    client.main()
    captured = capsys.readouterr()
    assert '"answers": ["a1", "a2"]' in captured.out
