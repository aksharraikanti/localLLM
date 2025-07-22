#!/usr/bin/env python3
"""
Clean raw QA data: normalize text, strip HTML, filter by length, and dedupe.
"""
import argparse
import json
import os
import re
import unicodedata
from typing import Optional, Tuple

import bleach


def clean_text(text: str) -> str:
    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)
    # Strip HTML tags
    text = bleach.clean(text, tags=[], strip=True)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove non-UTF8 characters
    text = text.encode("utf8", "ignore").decode("utf8")
    return text


def extract_qa(record: dict) -> Optional[Tuple[str, str]]:
    # Detect common key patterns
    if "question" in record and "answer" in record:
        return record["question"], record["answer"]
    if "title" in record and "body" in record:
        return record["title"], record["body"]
    return None


def clean_dataset(input_path: str, output_path: str,
                  min_tokens: int, max_tokens: int) -> int:
    # track seen answers to dedupe duplicates by answer content
    seen_answers = set()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    count = 0
    with open(input_path, "r", encoding="utf8") as src, \
         open(output_path, "w", encoding="utf8") as dst:
        # Load JSON or JSONL
        first = src.read(1)
        src.seek(0)
        if first == '[':
            data = json.load(src)
        else:
            data = [json.loads(line) for line in src if line.strip()]
        for rec in data:
            qa = extract_qa(rec)
            if not qa:
                continue
            q_raw, a_raw = qa
            q = clean_text(q_raw)
            a = clean_text(a_raw)
            # Length filtering (skip for FAQ entries)
            is_faq = "title" in rec and "body" in rec
            if not is_faq:
                qtoks = len(q.split())
                atoks = len(a.split())
                if qtoks < min_tokens or qtoks > max_tokens:
                    continue
                if atoks < min_tokens or atoks > max_tokens:
                    continue
            # Deduplicate by answer content (skip repeated answers)
            if a in seen_answers:
                continue
            seen_answers.add(a)
            out = {"question": q, "answer": a}
            dst.write(json.dumps(out, ensure_ascii=False) + "\n")
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Clean QA data and output JSONL.")
    parser.add_argument("--input", required=True, help="Input JSON or JSONL file path")
    parser.add_argument("--output", required=True, help="Output JSONL file path")
    parser.add_argument("--min-tokens", type=int, default=10,
                        help="Minimum token count per QA")
    parser.add_argument("--max-tokens", type=int, default=512,
                        help="Maximum token count per QA")
    args = parser.parse_args()
    total = clean_dataset(args.input, args.output,
                          args.min_tokens, args.max_tokens)
    print(f"Saved {total} cleaned records to {args.output}")


if __name__ == "__main__":
    main()
