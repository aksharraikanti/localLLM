import pytest

from src.triton_tune import TRITON_AVAILABLE, main, tune_triton


def test_tune_triton_not_installed(monkeypatch):
    # Simulate missing triton
    monkeypatch.setattr("src.triton_tune.TRITON_AVAILABLE", False)
    with pytest.raises(RuntimeError):
        tune_triton("model_dir", [])


def test_main_skip_tuning(monkeypatch, capsys):
    # Simulate missing triton to hit the skip path
    monkeypatch.setattr("src.triton_tune.TRITON_AVAILABLE", False)
    monkeypatch.setattr("sys.argv", ["triton_tune.py", "--model-dir", "m"])
    main()
    captured = capsys.readouterr()
    assert "Triton not available; skipping tuning." in captured.out
