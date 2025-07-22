import json

import pytest

from scripts.clean_data import clean_text, clean_dataset, extract_qa


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Some\u212b text", "SomeÅ text"),  # NFKC normalization
        ("<p>Hello  <b>World</b>!</p>", "Hello World!"),
        ("Line1\n\nLine2", "Line1 Line2"),
    ],
)
def test_clean_text(raw, expected):
    assert clean_text(raw) == expected


def test_extract_qa():
    rec1 = {"question": "Q?", "answer": "A."}
    rec2 = {"title": "Q?", "body": "A."}
    rec3 = {"foo": 1}
    assert extract_qa(rec1) == ("Q?", "A.")
    assert extract_qa(rec2) == ("Q?", "A.")
    assert extract_qa(rec3) is None


def test_clean_dataset(tmp_path):
    data = [
        {"question": "Q1? Q1? Q1? Q1? Q1? Q1? Q1? Q1? Q1? Q1?", "answer": "A1 A1 A1 A1 A1 A1 A1 A1 A1 A1"},
        {"question": "short", "answer": "short"},
        {"title": "<b>Q2?</b>", "body": "<p>A2</p>"},
        {"question": "Dup? Dup? Dup? Dup? Dup? Dup? Dup? Dup? Dup? Dup?", "answer": "A1 A1 A1 A1 A1 A1 A1 A1 A1 A1"},
    ]
    infile = tmp_path / "in.json"
    outfile = tmp_path / "out.jsonl"
    infile.write_text(json.dumps(data), encoding="utf8")
    count = clean_dataset(str(infile), str(outfile), min_tokens=10, max_tokens=20)
    lines = outfile.read_text(encoding="utf8").splitlines()
    assert count == 2
    results = [json.loads(l) for l in lines]
    # Expect first and third (title/body) cleaned entries, deduped
    assert results[0]["question"].startswith("Q1?")
    assert results[1]["question"] == "Q2?"
