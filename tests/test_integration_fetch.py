import os

import pytest

from scripts.fetch_stackexchange import fetch_questions


@pytest.mark.skipif(
    not os.getenv("STACKEX_API_KEY"),
    reason="Requires STACKEX_API_KEY for integration test",
)
def test_integration_fetch_questions():
    # Perform a minimal fetch to verify live API connectivity
    data = fetch_questions(
        tags=["kubernetes"], page_size=1, api_key=os.getenv("STACKEX_API_KEY")
    )
    assert isinstance(data, list)
    assert len(data) == 1
    assert "question_id" in data[0] or "question_id" in data[0]
