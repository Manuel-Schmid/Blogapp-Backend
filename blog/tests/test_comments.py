from typing import Callable
import pytest


@pytest.mark.django_db
def test_create_comments(
    create_comments: Callable, import_query: Callable, client_query: Callable
) -> None:
    assert len(create_comments()) == 2
