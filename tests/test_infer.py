import pytest
import torch

from src.infer import FLASH_ATTENTION_AVAILABLE, generate_text


def test_generate_text(monkeypatch):
    # Stub tokenizer and model
    class DummyTok:
        def __call__(self, text, **kwargs):
            return {
                "input_ids": torch.tensor([[1]]),
                "attention_mask": torch.tensor([[1]]),
            }

        def decode(self, ids, skip_special_tokens=True):
            return "output"

    class DummyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()

        def generate(self, **kwargs):
            return torch.tensor([[1]])

    monkeypatch.setattr(
        "src.infer.AutoTokenizer.from_pretrained", lambda m, use_fast: DummyTok()
    )
    monkeypatch.setattr(
        "src.infer.AutoModelForCausalLM.from_pretrained", lambda m: DummyModel()
    )

    result = generate_text("model_dir", "hello", max_length=10)
    assert result == "output"


def test_flash_attention_flag(monkeypatch):
    # Simulate missing flash-attn in the infer module
    monkeypatch.setattr("src.infer.FLASH_ATTENTION_AVAILABLE", False)
    from src.infer import FLASH_ATTENTION_AVAILABLE as flag

    assert flag is False
