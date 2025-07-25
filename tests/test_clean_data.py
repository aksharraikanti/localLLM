import json

import pytest

from scripts.clean_data import clean_dataset, clean_text, extract_qa


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Some\u212b text", "SomeÅ text"),  # NFKC normalization
        ("<p>Hello <b>World</b>!</p>", "Hello World!"),
        ("Line1\n\nLine2", "Line1 Line2"),
    ],
)
def test_clean_text(raw, expected):
    assert clean_text(raw) == expected


@pytest.mark.parametrize(
    "record,expected",
    [
        ({"question": "Q?", "answer": "A."}, ("Q?", "A.")),
        ({"title": "Q?", "body": "A."}, ("Q?", "A.")),
        ({"foo": 1}, None),
    ],
)
def test_extract_qa(record, expected):
    assert extract_qa(record) == expected


def test_clean_dataset(tmp_path):
    # Prepare sample data
    data = [
        {"question": "Q1 " * 10, "answer": "A1 " * 10},
        {"question": "short", "answer": "short"},
        {"title": "<b>Q2?</b>", "body": "<p>A2</p>"},
        {"question": "Q1 " * 10, "answer": "A1 " * 10},  # duplicate
    ]
    infile = tmp_path / "in.json"
    outfile = tmp_path / "out.jsonl"
    infile.write_text(json.dumps(data), encoding="utf8")

    count = clean_dataset(str(infile), str(outfile), min_tokens=10, max_tokens=100)
    lines = outfile.read_text(encoding="utf8").splitlines()
    assert count == 2
    results = [json.loads(l) for l in lines]
    # Expect first cleaned Q1+A1 and third Q2+A2
    assert results[0]["question"].startswith("Q1")
    assert results[1]["question"] == "Q2?"
