#!/usr/bin/env python3
"""
Fetch Q&A data from the Stack Exchange API based on tags.
"""

import argparse
import json
import os


def fetch_questions(tags, page_size, api_key, access_token):
    """
    Fetch questions from Stack Exchange matching the given tags.

    Args:
        tags (list[str]): List of tag strings to filter questions.
        page_size (int): Number of questions per page.
        api_key (str): Stack Exchange API key.
        access_token (str): OAuth access token, if required.

    Returns:
        list[dict]: Raw question data from API.
    """
    raise NotImplementedError("Function fetch_questions is not implemented yet.")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Stack Exchange questions by tags",
    )
    parser.add_argument(
        "--tags",
        nargs="+",
        required=True,
        help="List of tags to query (e.g., kubernetes networking)",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="Number of questions to fetch per page",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path for the raw JSON data",
    )
    args = parser.parse_args()

    api_key = os.getenv("STACKEX_API_KEY")
    access_token = os.getenv("STACKEX_ACCESS_TOKEN")
    if not api_key:
        parser.error("Environment variable STACKEX_API_KEY is required.")

    data = fetch_questions(
        tags=args.tags,
        page_size=args.page_size,
        api_key=api_key,
        access_token=access_token,
    )
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
