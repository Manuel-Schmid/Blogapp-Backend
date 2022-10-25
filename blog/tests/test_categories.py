from typing import Callable, Dict
import pytest
from strawberry.test import Response


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_categories(
    create_categories: Callable, import_query: Callable, client_query: Callable
) -> None:
    assert len(create_categories()) == 2


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_category(import_query: Callable, client_query: Callable) -> None:
    category_input = {
        "categoryInput": {
            "name": "test_category",
        }
    }
    query: str = import_query('createCategory.graphql')
    client_query(query, category_input)
    response: Response = client_query(query, category_input)

    assert response is not None
    assert response.errors is None

    create_category: Dict = response.data.get('createCategory', None)
    assert create_category is not None

    category_id: Dict = create_category.get('id', None)
    assert category_id is not None
    assert category_id == "2"

    category_slug: Dict = create_category.get('slug', None)
    assert category_slug is not None
    assert category_slug == "test_category-2"


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_category_too_long_fields(
    import_query: Callable, client_query: Callable
) -> None:
    category_input = {
        "categoryInput": {
            "name": "e" * 201,
        }
    }
    query: str = import_query('createCategory.graphql')
    response: Response = client_query(query, category_input)

    assert response is not None

    create_category: Dict = response.data.get('createCategory', None)
    assert create_category is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_update_category(
    create_categories: Callable, import_query: Callable, client_query: Callable
) -> None:
    create_categories()
    category_input = {"categoryInput": {"id": 2, "name": "test_category3"}}

    query: str = import_query('updateCategory.graphql')
    client_query(query, category_input)
    response: Response = client_query(query, category_input)

    assert response is not None
    assert response.errors is None

    update_category: Dict = response.data.get('updateCategory', None)
    assert update_category is not None

    category_id: Dict = update_category.get('id', None)
    assert category_id is not None
    assert category_id == "2"

    category_name: Dict = update_category.get('name', None)
    assert category_name is not None
    assert category_name == "test_category3"
