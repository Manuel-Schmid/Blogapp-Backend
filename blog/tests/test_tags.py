from typing import Callable
import pytest


@pytest.mark.django_db
def test_create_tags(
    create_tags: Callable, import_query: Callable, client_query: Callable
) -> None:
    assert len(create_tags()) == 3
