import os

import pytest

from src.export_onnx import main as export_main


def test_export_onnx_dry_run(monkeypatch, tmp_path, capsys):
    model_dir = tmp_path / "model"
    onnx_out = tmp_path / "model.onnx"
    # create dummy model directory
    model_dir.mkdir()

    # stub ONNX convert function
    # stub convert function
    monkeypatch.setattr(
        "src.export_onnx.onnx_exporter.convert", lambda model, output, **kw: None
    )
    os.makedirs(onnx_out.parent, exist_ok=True)
    # run script
    args = [
        "export_onnx.py",
        "--model-dir",
        str(model_dir),
        "--output",
        str(onnx_out),
    ]
    monkeypatch.setattr("sys.argv", args)
    export_main()
    captured = capsys.readouterr()
    assert f"ONNX model exported to {onnx_out}" in captured.out
