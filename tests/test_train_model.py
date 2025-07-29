import pytest

from scripts.train_model import train_model


class DummyModel:
    def __init__(self):
        self.saved = None

    def save_model(self, output_dir):
        self.saved = output_dir


class DummyTokenizer:
    pass


def test_train_model_flow(monkeypatch, tmp_path):
    # Prepare dummy dataset directory
    ds_dir = tmp_path / "dataset"
    ds_dir.mkdir()

    # Mock load_from_disk
    monkeypatch.setattr("scripts.train_model.load_from_disk", lambda path: "dummy-ds")
    # Mock tokenizer and model
    # Stub tokenizer.from_pretrained for tests
    monkeypatch.setattr(
        "scripts.train_model.AutoTokenizer.from_pretrained",
        lambda *args, **kwargs: DummyTokenizer(),
    )
    dummy_model = DummyModel()
    # Stub model.from_pretrained for tests
    monkeypatch.setattr(
        "scripts.train_model.AutoModelForSeq2SeqLM.from_pretrained",
        lambda *args, **kwargs: dummy_model,
    )
    # Mock data collator
    monkeypatch.setattr(
        "scripts.train_model.DataCollatorForSeq2Seq", lambda **kwargs: "collator"
    )
    # Capture Trainer calls
    calls = {}

    class DummyTrainer:
        def __init__(self, model, args, train_dataset, data_collator, tokenizer):
            calls["model"] = model
            calls["dataset"] = train_dataset
            calls["collator"] = data_collator
            calls["tokenizer"] = tokenizer

        def train(self):
            calls["trained"] = True

        def save_model(self, output_dir):
            calls["saved"] = output_dir

    monkeypatch.setattr("scripts.train_model.Trainer", DummyTrainer)
    monkeypatch.setattr(
        "scripts.train_model.TrainingArguments", lambda **kwargs: kwargs
    )

    out_dir = tmp_path / "out"
    train_model(
        dataset_dir=str(ds_dir),
        model_name_or_path="dummy",
        output_dir=str(out_dir),
        per_device_train_batch_size=1,
        num_train_epochs=1,
        learning_rate=1e-4,
    )
    assert calls.get("trained") is True
    assert calls.get("saved") == str(out_dir)
