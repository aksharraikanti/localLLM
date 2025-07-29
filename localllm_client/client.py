#!/usr/bin/env python3
"""
Simple CLI client for the QA inference API.
"""
import argparse
import json
import os

import requests


def main():
    parser = argparse.ArgumentParser(description="Client for QA Inference API")
    parser.add_argument(
        "--url", default="http://localhost:8000", help="Base URL of the inference API"
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("API_KEY"),
        help="API key for authentication",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--question", help="Single question to query")
    group.add_argument(
        "--batch-file",
        help="Path to JSON file with {'questions': [...] } for batch inference",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=512,
        help="Maximum generation length",
    )
    args = parser.parse_args()

    headers = {}
    if args.api_key:
        headers["X-API-Key"] = args.api_key

    if args.question:
        payload = {"question": args.question, "max_length": args.max_length}
        endpoint = f"{args.url.rstrip('/')}/predict"
    else:
        with open(args.batch_file, encoding="utf8") as f:
            payload = json.load(f)
        payload.setdefault("max_length", args.max_length)
        endpoint = f"{args.url.rstrip('/')}/predict_batch"

    resp = requests.post(endpoint, json=payload, headers=headers)
    resp.raise_for_status()
    try:
        data = resp.json()
        print(json.dumps(data))
    except ValueError:
        print(resp.text)


if __name__ == "__main__":
    main()
