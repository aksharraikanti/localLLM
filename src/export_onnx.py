#!/usr/bin/env python3
"""
Export a quantized model to ONNX for accelerated generation.
"""
import argparse

from optimum.exporters import onnx as onnx_exporter


def main():
    parser = argparse.ArgumentParser(description="Export model to ONNX format")
    parser.add_argument(
        "--model-dir",
        required=True,
        help="Path to the quantized model directory",
    )
    parser.add_argument(
        "--output",
        default="onnx/llama2_quantized.onnx",
        help="Output ONNX model path",
    )
    args = parser.parse_args()

    # Perform export; requires optimum and onnxruntime
    onnx_exporter.convert(
        model=args.model_dir,
        output=args.output,
        feature="generation",
        opset=13,
        use_gpu=False,
    )
    print(f"ONNX model exported to {args.output}")


if __name__ == "__main__":
    main()
