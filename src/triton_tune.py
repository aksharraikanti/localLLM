#!/usr/bin/env python3
"""
Triton kernel tuning harness for inference acceleration.
"""
import argparse

try:
    import triton

    TRITON_AVAILABLE = True
except ImportError:
    TRITON_AVAILABLE = False

from typing import List


def tune_triton(
    model_dir: str, prompts: List[str], max_length: int = 128, runs: int = 5
):
    """
    Compile the model.generate function with Torch-Triton backend and measure inference speed.

    Returns a dict with 'warmup_time', 'avg_latency_ms', and 'compiled' flag.
    """
    if not TRITON_AVAILABLE:
        raise RuntimeError("Triton is not installed; cannot tune kernels.")
    import torch

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(model_dir).to(device)

    # Prepare generate function and compile with TorchDynamo/Triton
    gen = model.generate
    try:
        compiled_gen = torch.compile(gen, backend="inductor")
        compiled = True
    except Exception:
        compiled_gen = gen
        compiled = False

    # Warm-up runs
    prompt = prompts[0] if prompts else "Hello"
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    t0 = time.time()
    for _ in range(2):
        _ = compiled_gen(**inputs, max_length=max_length)
    warmup = (time.time() - t0) * 1000

    # Timed runs
    latencies = []
    for _ in range(runs):
        t1 = time.time()
        _ = compiled_gen(**inputs, max_length=max_length)
        latencies.append((time.time() - t1) * 1000)
    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
    return {"compiled": compiled, "warmup_ms": warmup, "avg_latency_ms": avg_lat}


def main():
    parser = argparse.ArgumentParser(
        description="Run Triton (Torch-Triton) tuning for inference."
    )
    parser.add_argument(
        "--model-dir", required=True, help="Path to model directory for tuning"
    )
    parser.add_argument(
        "--prompts",
        required=False,
        help="JSON file with {'prompts': [...] } to tune on",
    )
    parser.add_argument(
        "--max-length", type=int, default=128, help="Max generation length"
    )
    parser.add_argument("--runs", type=int, default=5, help="Number of timed runs")
    args = parser.parse_args()
    if not TRITON_AVAILABLE:
        print("Triton not available; skipping tuning.")
        return

    # load prompts if provided
    if args.prompts:
        from src.quantize import load_prompts

        prompts = load_prompts(args.prompts)
    else:
        prompts = []

    print("Triton available; starting kernel tuning and timing...")
    stats = tune_triton(
        args.model_dir, prompts, max_length=args.max_length, runs=args.runs
    )
    print(f"Compiled: {stats['compiled']}")
    print(f"Warm-up time (ms): {stats['warmup_ms']:.2f}")
    print(f"Average latency (ms): {stats['avg_latency_ms']:.2f}")


if __name__ == "__main__":
    main()
