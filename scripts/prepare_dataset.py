#!/usr/bin/env python3
"""
Prepare a Hugging Face dataset from cleaned JSONL for model fine-tuning.
"""
import argparse
import os

from datasets import load_dataset
from transformers import AutoTokenizer


def prepare_dataset(
    input_path: str, output_dir: str, model_name_or_path: str, max_length: int
):
    """
    Load a JSONL file, tokenize questions and answers, and save dataset to disk.
    """
    os.makedirs(output_dir, exist_ok=True)
    ds = load_dataset("json", data_files={"train": input_path}, split="train")
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)

    def tokenize_fn(example):
        inputs = example["question"]
        targets = example["answer"]
        model_inputs = tokenizer(inputs, max_length=max_length, truncation=True)
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(targets, max_length=max_length, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized = ds.map(
        tokenize_fn,
        batched=True,
        remove_columns=ds.column_names,
    )
    tokenized.save_to_disk(output_dir)
    print(f"Saved tokenized dataset to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare dataset for model fine-tuning"
    )
    parser.add_argument(
        "--input",
        default="data/clean/combined.jsonl",
        help="Combined JSONL input file",
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed/dataset",
        help="Directory to write tokenized dataset",
    )
    parser.add_argument(
        "--model-name-or-path",
        required=True,
        help="Model name or path for tokenizer",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=512,
        help="Max sequence length after tokenization",
    )
    args = parser.parse_args()
    prepare_dataset(
        args.input, args.output_dir, args.model_name_or_path, args.max_length
    )


if __name__ == "__main__":
    main()
