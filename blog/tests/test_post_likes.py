from typing import Callable
import pytest


@pytest.mark.django_db
def test_create_post_likes(
    create_post_likes: Callable, import_query: Callable, client_query: Callable
) -> None:
    assert len(create_post_likes()) == 2
