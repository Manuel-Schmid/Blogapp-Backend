from typing import Callable, Dict
import pytest
from strawberry.test import Response


@pytest.mark.django_db
def test_create_tags(
    create_tags: Callable, import_query: Callable, client_query: Callable
) -> None:
    assert len(create_tags()) == 3


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_get_all_tags(
    create_tags: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_tags()

    query: str = import_query('allTags.graphql')
    response: Response = client_query(query)

    assert response is not None
    assert response.errors is None

    tags: Dict = response.data.get('tags', None)
    assert tags is not None
    assert len(tags) == 3
    tag1_slug = tags[0].get('slug', None)
    assert tag1_slug is not None
    assert tag1_slug == 'tag_1_slug'
    tag2_slug = tags[1].get('slug', None)
    assert tag2_slug is not None
    assert tag2_slug == 'tag_2_slug'
    tag3_slug = tags[2].get('slug', None)
    assert tag3_slug is not None
    assert tag3_slug == 'tag_3_slug'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_get_all_used_tags(
    create_tags: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_tags()

    query: str = import_query('usedTags.graphql')
    response: Response = client_query(query)

    assert response is not None
    assert response.errors is None

    tags: Dict = response.data.get('usedTags', None)
    assert tags is not None
    assert len(tags) == 2
    tag1_slug = tags[0].get('slug', None)
    assert tag1_slug is not None
    assert tag1_slug == 'tag_1_slug'
    tag2_slug = tags[1].get('slug', None)
    assert tag2_slug is not None
    assert tag2_slug == 'tag_2_slug'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_get_used_tags_in_category(
    create_tags: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_tags()

    category_slug = {"categorySlug": "test_category2"}

    query: str = import_query('usedTags.graphql')
    response: Response = client_query(query, category_slug)

    assert response is not None
    assert response.errors is None

    tags: Dict = response.data.get('usedTags', None)
    assert tags is not None
    assert len(tags) == 1
    tag1_slug = tags[0].get('slug', None)
    assert tag1_slug is not None
    assert tag1_slug == 'tag_2_slug'
