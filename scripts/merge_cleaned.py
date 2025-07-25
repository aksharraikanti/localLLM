#!/usr/bin/env python3
"""
Merge all cleaned JSONL files under data/clean/ into a single combined JSONL.
"""

import argparse
import glob
import json
import os


def merge_cleaned(input_dir: str, output_path: str) -> int:
    """
    Merge all JSONL files in input_dir into output_path.

    Returns the total number of records merged.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    count = 0
    with open(output_path, "w", encoding="utf8") as out_f:
        for path in glob.glob(os.path.join(input_dir, "*.jsonl")):
            with open(path, "r", encoding="utf8") as in_f:
                for line in in_f:
                    out_f.write(line)
                    count += 1
    return count


def main():
    parser = argparse.ArgumentParser(
        description="Merge cleaned JSONL files into combined dataset"
    )
    parser.add_argument(
        "--input-dir", default="data/clean", help="Directory of cleaned JSONL files"
    )
    parser.add_argument(
        "--output",
        default="data/clean/combined.jsonl",
        help="Output combined JSONL path",
    )
    args = parser.parse_args()
    total = merge_cleaned(args.input_dir, args.output)
    print(f"Merged {total} records into {args.output}")


if __name__ == "__main__":
    main()
