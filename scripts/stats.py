#!/usr/bin/env python3
"""
Compute dataset statistics: average tokens in question/answer and vocabulary size.
"""

import argparse
import json
from collections import Counter


def compute_stats(input_path: str):
    """
    Read JSONL from input_path and compute stats.

    Returns a dict with average question tokens, average answer tokens, and vocab size.
    """
    total_q_tokens = 0
    total_a_tokens = 0
    total = 0
    vocab = Counter()
    with open(input_path, "r", encoding="utf8") as f:
        for line in f:
            rec = json.loads(line)
            q = rec.get("question", "")
            a = rec.get("answer", "")
            q_tokens = q.split()
            a_tokens = a.split()
            total_q_tokens += len(q_tokens)
            total_a_tokens += len(a_tokens)
            total += 1
            vocab.update(q_tokens)
            vocab.update(a_tokens)
    return {
        "num_records": total,
        "avg_q_tokens": total_q_tokens / total if total else 0,
        "avg_a_tokens": total_a_tokens / total if total else 0,
        "vocab_size": len(vocab),
    }


def main():
    parser = argparse.ArgumentParser(description="Compute stats for cleaned dataset")
    parser.add_argument(
        "--input", default="data/clean/combined.jsonl", help="Input combined JSONL file"
    )
    parser.add_argument(
        "--output",
        default="data/processed/stats.md",
        help="Output markdown file for stats",
    )
    args = parser.parse_args()
    stats = compute_stats(args.input)
    with open(args.output, "w", encoding="utf8") as f:
        f.write(f"# Dataset Statistics\n")
        f.write(f"- Number of records: {stats['num_records']}\n")
        f.write(f"- Average question tokens: {stats['avg_q_tokens']:.2f}\n")
        f.write(f"- Average answer tokens: {stats['avg_a_tokens']:.2f}\n")
        f.write(f"- Vocabulary size: {stats['vocab_size']}\n")
    print(f"Wrote stats to {args.output}")


if __name__ == "__main__":
    main()
