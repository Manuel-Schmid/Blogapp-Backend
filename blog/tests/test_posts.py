from typing import Callable
import pytest


@pytest.mark.django_db
def test_create_posts(
    create_posts: Callable, import_query: Callable, client_query: Callable
) -> None:
    assert len(create_posts()) == 2
