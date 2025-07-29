import pytest
from fastapi import FastAPI

import scripts.run_inference_api as api


@pytest.fixture(autouse=True)
def clear_model(monkeypatch):
    # Ensure model/tokenizer are unset for tests
    monkeypatch.setattr(api, "tokenizer", None)
    monkeypatch.setattr(api, "model", None)
    return api


def test_app_instance():
    assert isinstance(api.app, FastAPI)


def test_predict_not_ready():
    from fastapi.testclient import TestClient

    client = TestClient(api.app)
    response = client.post("/predict", json={"question": "Hello"})
    assert response.status_code == 503


def test_predict_smoke(monkeypatch):
    # stub tokenizer and model for smoke test
    class DummyTok:
        def __call__(self, text, **kwargs):
            return {"input_ids": [0], "attention_mask": [0]}

        def decode(self, ids, skip_special_tokens=True):
            return "dummy"

    class DummyModel:
        def generate(self, input_ids, attention_mask, max_length):
            return [[0]]

    monkeypatch.setattr(api, "tokenizer", DummyTok())
    monkeypatch.setattr(api, "model", DummyModel())
    from fastapi.testclient import TestClient

    client = TestClient(api.app)
    response = client.post("/predict", json={"question": "Test question"})
    assert response.status_code == 200
    assert response.json() == {"answer": "dummy"}
