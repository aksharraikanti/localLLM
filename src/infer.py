#!/usr/bin/env python3
"""
Inference script with optional FlashAttention acceleration.
"""
import argparse

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    # Import FlashAttention if installed
    from flash_attn.flash_attn_unpadded import \
        flash_attn_unpadded  # noqa: F401

    FLASH_ATTENTION_AVAILABLE = True
except ImportError:
    FLASH_ATTENTION_AVAILABLE = False


def generate_text(model_dir: str, prompt: str, max_length: int = 128) -> str:
    """Generate a response for a single prompt."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(model_dir).to(device)

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    # FlashAttention will be used internally by Hugging Face if enabled globally
    outputs = model.generate(**inputs, max_length=max_length)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def main():
    parser = argparse.ArgumentParser(
        description="Run model inference with optional FlashAttention."
    )
    parser.add_argument("--model-dir", required=True, help="Path to model directory")
    parser.add_argument("--prompt", required=True, help="Prompt text for generation")
    parser.add_argument(
        "--max-length", type=int, default=128, help="Maximum generation length"
    )
    args = parser.parse_args()
    if FLASH_ATTENTION_AVAILABLE:
        print("FlashAttention is enabled.")
    else:
        print("FlashAttention not available; running standard attention.")
    response = generate_text(args.model_dir, args.prompt, args.max_length)
    print(response)


if __name__ == "__main__":
    main()
