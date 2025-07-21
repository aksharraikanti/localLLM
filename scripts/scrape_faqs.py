#!/usr/bin/env python3
"""
Scrape FAQ pages for simple Q&A extraction.
"""
import argparse
import json
import time
import requests
from bs4 import BeautifulSoup

def scrape_faq_page(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    faqs = []
    for header in soup.find_all(['h2', 'h3']):
        question = header.get_text(strip=True)
        answer_parts = []
        for sib in header.find_next_siblings():
            if sib.name in ['h2', 'h3']:
                break
            if sib.name == 'p':
                answer_parts.append(sib.get_text(strip=True))
        if answer_parts:
            faqs.append({"question": question, "answer": " ".join(answer_parts)})
    return faqs

def main():
    parser = argparse.ArgumentParser(description="Scrape FAQ pages for Q&A pairs")
    parser.add_argument("--urls", required=True, nargs='+', help="List of FAQ page URLs")
    parser.add_argument("--output", default="data/raw/faqs.json")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")
    args = parser.parse_args()
    all_faqs = []
    for url in args.urls:
        print(f"Scraping {url}")
        faqs = scrape_faq_page(url)
        all_faqs.extend(faqs)
        time.sleep(args.delay)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(all_faqs, f, indent=2)
    print(f"Saved {len(all_faqs)} entries to {args.output}")

if __name__ == "__main__":
    main()
