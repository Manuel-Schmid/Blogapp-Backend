from typing import Callable, Dict
import pytest
from strawberry.test import Response


@pytest.mark.django_db
def test_create_posts(create_posts: Callable) -> None:
    assert len(create_posts()) == 2


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_post(
    auth: Callable,
    create_categories: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    create_categories()
    post_input = {
        'postInput': {
            'title': 'test_post',
            'text': 'this a test',
            'category': 2,
        }
    }

    query: str = import_query('createPost.graphql')
    response: Response = client_query(query, post_input)

    assert response is not None
    assert response.errors is None

    create_post: Dict = response.data.get('createPost', None)
    assert create_post is not None

    post_title: Dict = create_post.get('title', None)
    assert post_title is not None
    assert post_title == 'test_post'

    post_slug: Dict = create_post.get('slug', None)
    assert post_slug is not None
    assert post_slug == 'test_post'

    post_owner: Dict = create_post.get('owner', None)
    assert post_owner is not None
    assert post_owner.get('username', None) == 'jane.doe@blogapp.lo'

    post_category: Dict = create_post.get('category', None)
    assert post_category is not None
    assert post_category.get('slug', None) == 'test_category2'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_post_too_long_fields(
    auth: Callable,
    create_categories: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    create_categories()
    post_input = {
        'postInput': {
            'title': 'e' * 201,
            'text': 'this a test',
            'category': 2,
        }
    }

    query: str = import_query('createPost.graphql')
    response: Response = client_query(query, post_input)

    assert response is not None
    assert response.errors is None

    create_post: Dict = response.data.get('createPost', None)
    assert create_post is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_post_invalid_owner_id(
    create_categories: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_categories()
    post_input = {
        'postInput': {
            'title': 'test_post',
            'text': 'this a test',
            'category': 2,
        }
    }

    query: str = import_query('createPost.graphql')
    response: Response = client_query(query, post_input)

    assert response is not None
    assert response.errors is not None

    assert len(response.errors) > 0
    error_msg: Dict = response.errors[0]
    assert error_msg.get('message', None) == 'You do not have permission to perform this action'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_post_invalid_category_id(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    post_input = {
        'postInput': {
            'title': 'test_post',
            'text': 'this a test',
            'category': 1,
        }
    }

    query: str = import_query('createPost.graphql')
    response: Response = client_query(query, post_input)

    assert response is not None
    assert response.errors is None

    create_post: Dict = response.data.get('createPost', None)
    assert create_post is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_update_post(
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    post_input = {
        'postInput': {
            'slug': 'test_post-1',
            'title': 'Test_post3',
            'text': 'New Text',
            'category': 2,
            'owner': 2,
        }
    }

    query: str = import_query('updatePost.graphql')
    response: Response = client_query(query, post_input)

    assert response is not None
    assert response.errors is None

    update_post: Dict = response.data.get('updatePost', None)
    assert update_post is not None

    post_title: Dict = update_post.get('title', None)
    assert post_title is not None
    assert post_title == 'Test_post3'

    post_slug: Dict = update_post.get('slug', None)
    assert post_slug is not None
    assert post_slug == 'test_post-1'

    post_owner: Dict = update_post.get('owner', None)
    assert post_owner is not None
    assert post_owner.get('username', None) == 'test_user2'

    post_category: Dict = update_post.get('category', None)
    assert post_category is not None
    assert post_category.get('slug', None) == 'test_category2'
