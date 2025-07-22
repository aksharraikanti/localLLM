#!/usr/bin/env python3
"""
Fetch Q&A data from the Stack Exchange API based on tags.
"""

import argparse
import json
import os
import time

import requests


def fetch_questions(tags, page_size, api_key, access_token=None):
    """
    Fetch questions from Stack Exchange matching given tags with pagination.

    Args:
        tags (list[str]): Tags to filter questions (semicolon-separated).
        page_size (int): Questions per page (max 100).
        api_key (str): Stack Exchange API key.
        access_token (str, optional): OAuth access token.

    Returns:
        list[dict]: Aggregated question data from API.
    """
    url = "https://api.stackexchange.com/2.3/questions"
    params = {
        "order": "desc",
        "sort": "activity",
        "tagged": ";".join(tags),
        "site": "stackoverflow",
        "filter": "withbody",
        "pagesize": page_size,
        "page": 1,
        "key": api_key,
    }
    if access_token:
        params["access_token"] = access_token

    all_items = []
    while True:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        all_items.extend(items)
        if not data.get("has_more"):
            break
        params["page"] += 1
        time.sleep(1)
    return all_items


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Stack Exchange questions by tags",
    )
    parser.add_argument(
        "--tags",
        nargs="+",
        required=True,
        help="Tags to filter (e.g., kubernetes networking)",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="Number of questions to fetch per page (max 100)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path for raw question data",
    )
    args = parser.parse_args()

    api_key = os.getenv("STACKEX_API_KEY")
    access_token = os.getenv("STACKEX_ACCESS_TOKEN")
    if not api_key:
        parser.error("Environment variable STACKEX_API_KEY is required.")

    questions = fetch_questions(
        tags=args.tags,
        page_size=args.page_size,
        api_key=api_key,
        access_token=access_token,
    )
    output_dir = os.path.dirname(args.output)
    if output_dir:  # Ensure the directory part is not empty (e.g., for current directory files)
        os.makedirs(output_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
