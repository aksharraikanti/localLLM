import json

import pytest

from scripts.prepare_dataset import prepare_dataset


class DummyDataset:
    column_names = ["question", "answer"]

    def map(self, fn, batched, remove_columns):
        # Simulate tokenization mapping
        class Mapped:
            def save_to_disk(self, output_dir):
                pass

        return Mapped()


@pytest.fixture(autouse=True)
def patch_hf(monkeypatch, tmp_path):
    # Create a fake JSONL input
    data = [{"question": "Q?", "answer": "A."}]
    input_file = tmp_path / "sample.jsonl"
    with open(input_file, "w", encoding="utf8") as f:
        for rec in data:
            f.write(json.dumps(rec) + "\n")

    monkeypatch.setenv("HF_DATASETS_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setattr(
        "scripts.prepare_dataset.load_dataset", lambda *args, **kwargs: DummyDataset()
    )

    # Stub tokenizer.from_pretrained to avoid external dependencies
    class DummyTok:
        def as_target_tokenizer(self):
            return self

        def __call__(self, *args, **kwargs):
            return {}

    monkeypatch.setattr(
        "scripts.prepare_dataset.AutoTokenizer.from_pretrained",
        lambda model_name, use_fast=True: DummyTok(),
    )
    return input_file


def test_prepare_dataset_creates_output_dir(tmp_path, patch_hf):
    output_dir = tmp_path / "out"
    prepare_dataset(
        input_path=str(patch_hf),
        output_dir=str(output_dir),
        model_name_or_path="dummy-model",
        max_length=16,
    )
    assert output_dir.exists()
