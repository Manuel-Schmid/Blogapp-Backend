from typing import Callable
import pytest


@pytest.mark.django_db
def test_create_categories(
    create_categories: Callable, import_query: Callable, client_query: Callable
) -> None:
    create_categories()
