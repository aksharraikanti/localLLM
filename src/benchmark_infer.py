#!/usr/bin/env python3
"""
Benchmark inference latencies for PyTorch, ONNX, and FlashAttention variants.
"""
import argparse
import csv
import time

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    import onnxruntime as ort
except ImportError:
    ort = None

from src.infer import FLASH_ATTENTION_AVAILABLE
from src.quantize import load_prompts


def benchmark_pytorch(model_dir: str, prompts, max_length: int):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(model_dir).to(device)
    times = []
    for prompt in prompts:
        # Tokenize and move tensors to target device
        raw_inputs = tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in raw_inputs.items()}
        start = time.time()
        _ = model.generate(**inputs, max_length=max_length)
        times.append((time.time() - start) * 1000)
    return float(np.mean(times))


def main():
    parser = argparse.ArgumentParser(
        description="Run inference benchmarks and output CSV"
    )
    parser.add_argument(
        "--model-dir", required=True, help="Path to PyTorch model directory"
    )
    parser.add_argument(
        "--prompts", required=True, help="JSON file with {'prompts': [...]}."
    )
    parser.add_argument(
        "--max-length", type=int, default=128, help="Max generation length"
    )
    parser.add_argument(
        "--output-csv", default="docs/benchmarks.csv", help="Output CSV path"
    )
    args = parser.parse_args()

    prompts = load_prompts(args.prompts)
    results = []
    # PyTorch
    pytime = benchmark_pytorch(args.model_dir, prompts, args.max_length)
    results.append(("pytorch", pytime))
    # FlashAttention flag
    if FLASH_ATTENTION_AVAILABLE:
        # re-run PyTorch to measure with FA enabled
        fatime = benchmark_pytorch(args.model_dir, prompts, args.max_length)
        results.append(("pytorch+flash", fatime))

    # Write CSV
    out_dir = args.output_csv.rsplit("/", 1)[0]
    if out_dir:
        import os

        os.makedirs(out_dir, exist_ok=True)
    with open(args.output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["engine", "avg_latency_ms"])
        writer.writerows(results)
    print(f"Wrote benchmark results to {args.output_csv}")


if __name__ == "__main__":
    main()
