import json

import pytest

from src.quantize import evaluate_baseline, load_prompts


def test_load_prompts(tmp_path):
    prompts = {"prompts": ["Hello", "World"]}
    pfile = tmp_path / "prompts.json"
    pfile.write_text(json.dumps(prompts), encoding="utf8")
    loaded = load_prompts(str(pfile))
    assert loaded == prompts["prompts"]


@pytest.mark.parametrize("prompts", [["Hi"], []])
def test_evaluate_baseline_empty(monkeypatch, prompts):
    # Stub model and tokenizer
    class DummyModel:
        def __call__(self, **kwargs):
            class Out:
                loss = 0.0

            return Out()

        def generate(self, **kwargs):
            return [[0]]

        def to(self, device):
            return self

        def __getattr__(self, name):
            return lambda *args, **kwargs: None

    class DummyTok:
        def __call__(self, text, **kwargs):
            return {"input_ids": [0], "attention_mask": [1]}

        def decode(self, ids, skip_special_tokens=True):
            return "res"

    model = DummyModel()
    tokenizer = DummyTok()
    out = evaluate_baseline(model, tokenizer, prompts, max_length=10)
    assert isinstance(out, list)
    for r in out:
        assert "prompt" in r and "loss" in r and "response" in r
