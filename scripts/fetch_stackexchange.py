#!/usr/bin/env python3
"""
Fetch Q&A pairs from Stack Exchange API for specified tags.
"""
import argparse
import json
import os
import time
import requests

API_URL = "https://api.stackexchange.com/2.3/questions"

def fetch_questions(tags, pagesize=100, max_pages=10, key=None, access_token=None):
    all_items = []
    for page in range(1, max_pages + 1):
        params = {
            "order": "desc",
            "sort": "activity",
            "site": "stackoverflow",
            "tagged": tags,
            "pagesize": pagesize,
            "page": page,
            "filter": "withbody",
        }
        if key:
            params["key"] = key
        if access_token:
            params["access_token"] = access_token
        resp = requests.get(API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        if not items:
            break
        all_items.extend(items)
        if not data.get("has_more", False):
            break
        time.sleep(1)
    return all_items

def main():
    parser = argparse.ArgumentParser(description="Fetch StackExchange questions by tags")
    parser.add_argument("--tags", required=True, help="Comma-separated list of tags")
    parser.add_argument("--pagesize", type=int, default=100)
    parser.add_argument("--maxpages", type=int, default=10)
    parser.add_argument("--output", default="data/raw/stackexchange.json")
    args = parser.parse_args()
    key = os.getenv("STACKEX_API_KEY")
    token = os.getenv("STACKEX_ACCESS_TOKEN")
    items = fetch_questions(args.tags, args.pagesize, args.maxpages, key, token)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(items, f, indent=2)
    print(f"Saved {len(items)} records to {args.output}")

if __name__ == "__main__":
    main()
