#!/usr/bin/env python3
"""
Quantization and evaluation utilities for the LoRA adapter model.
"""
import argparse
import json
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def evaluate_baseline(model, tokenizer, prompts, max_length=128):
    """Compute perplexities and generate responses for a list of prompts."""
    results = []
    device = getattr(model, "device", torch.device("cpu"))
    for prompt in prompts:
        raw = tokenizer(prompt, return_tensors="pt")
        # move tensors to device if needed
        inputs = {
            k: v.to(device) if isinstance(v, torch.Tensor) else v
            for k, v in raw.items()
        }
        with torch.no_grad():
            output = model(**inputs, labels=inputs.get("input_ids", None))
            raw_loss = getattr(output, "loss", None)
            # support torch scalar or float
            loss = raw_loss.item() if hasattr(raw_loss, "item") else float(raw_loss)
            # generation
        gen = model.generate(**inputs, max_length=max_length)
        resp = tokenizer.decode(gen[0], skip_special_tokens=True)
        results.append({"prompt": prompt, "loss": loss, "response": resp})
    return results


def load_prompts(file_path):
    """Load JSON file with 'prompts': [str...]."""
    with open(file_path, "r", encoding="utf8") as f:
        data = json.load(f)
    return data.get("prompts", [])


def main():
    parser = argparse.ArgumentParser(
        description="Quantize model and evaluate baseline perplexity"
    )
    parser.add_argument(
        "--model-dir", required=True, help="Directory of fine-tuned adapter model"
    )
    parser.add_argument(
        "--prompts", required=True, help="JSON file with {'prompts': [...]}"
    )
    parser.add_argument(
        "--baseline-out",
        default="eval/baseline.json",
        help="Output JSON for baseline eval",
    )
    parser.add_argument(
        "--quant-out",
        default="models/quantized/8bit_model",
        help="Output dir for 8-bit model",
    )
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.baseline_out), exist_ok=True)

    # Load model and tokenizer in 8-bit mode for baseline
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_dir, load_in_8bit=True, device_map="auto"
    )

    prompts = load_prompts(args.prompts)
    baseline = evaluate_baseline(model, tokenizer, prompts)
    with open(args.baseline_out, "w", encoding="utf8") as f:
        json.dump(baseline, f, indent=2)

    # Save quantized model
    model.save_pretrained(args.quant_out)
    print(f"Saved 8-bit quantized model to {args.quant_out}")


if __name__ == "__main__":
    main()
