import pytest

from scripts.fetch_stackexchange import fetch_questions


def test_fetch_questions_not_implemented():
    """fetch_questions should raise NotImplementedError until implemented."""
    with pytest.raises(NotImplementedError):
        fetch_questions(
            tags=["kubernetes"],
            page_size=10,
            api_key="key",
            access_token="token",
        )
