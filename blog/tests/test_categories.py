from typing import Callable
import pytest


@pytest.mark.django_db
def test_create_categories(
    create_categories: Callable, import_query: Callable, client_query: Callable
) -> None:
    assert len(create_categories()) == 2


# @pytest.mark.django_db
# def test_create_category(import_query: Callable, client_query: Callable) -> None:
#     category_input = {
#         "categoryInput": {
#             "name": "test_category",
#         }
#     }
#     mutation: str = import_query('createCategory.graphql')
#     graphql_client.raw_query(mutation, category_input, asserts_errors=False)
#     response = graphql_client.raw_query(mutation, category_input, asserts_errors=False)
#
#     json_data: Dict = json.loads(response.content)
#     assert json_data.get('errors', None) is None
#
#     data: Dict = json_data.get('data', None)
#     assert data is not None
#
#     create_category: Dict = data.get('createCategory', None)
#     assert create_category is not None
#
#     category_id: Dict = create_category.get('id', None)
#     assert category_id is not None
#     assert category_id == "2"
