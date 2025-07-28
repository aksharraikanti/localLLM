#!/usr/bin/env python3
"""
Run evaluation of a fine-tuned Seq2Seq model on a cleaned QA dataset and compute ROUGE metrics.
"""
import argparse
import json

import evaluate
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def load_qa_pairs(input_path: str):
    """Load question-answer pairs from a JSONL file."""
    qa_pairs = []
    with open(input_path, encoding="utf8") as f:
        for line in f:
            rec = json.loads(line)
            qa_pairs.append((rec.get("question", ""), rec.get("answer", "")))
    return qa_pairs


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Seq2Seq model with ROUGE metrics"
    )
    parser.add_argument(
        "--input",
        default="data/clean/combined.jsonl",
        help="Input cleaned JSONL file with question/answer pairs",
    )
    parser.add_argument(
        "--model-dir",
        required=True,
        help="Directory of the fine-tuned model to evaluate",
    )
    parser.add_argument(
        "--output",
        default="data/processed/eval_report.md",
        help="Output markdown report path",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for generation",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=512,
        help="Maximum generation length",
    )
    args = parser.parse_args()

    # Load data and metric
    qa_pairs = load_qa_pairs(args.input)
    questions, references = zip(*qa_pairs) if qa_pairs else ([], [])
    rouge = evaluate.load("rouge")

    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_dir)

    # Generate predictions
    predictions = []
    for i in range(0, len(questions), args.batch_size):
        batch_q = questions[i : i + args.batch_size]
        inputs = tokenizer(
            list(batch_q), return_tensors="pt", padding=True, truncation=True
        )
        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_length=args.max_length,
        )
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        predictions.extend(decoded)

    # Compute ROUGE scores
    results = rouge.compute(predictions=predictions, references=list(references))

    # Write report
    with open(args.output, "w", encoding="utf8") as report:
        report.write("# Evaluation Report\n")
        for metric_name, score in results.items():
            report.write(f"- {metric_name}: {score:.4f}\n")
    print(f"Wrote evaluation report to {args.output}")


if __name__ == "__main__":
    main()
