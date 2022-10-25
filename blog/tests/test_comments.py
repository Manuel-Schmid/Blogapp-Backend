from typing import Callable, Dict
import pytest
from strawberry.test import Response


@pytest.mark.django_db
def test_create_comments(
    create_comments: Callable, import_query: Callable, client_query: Callable
) -> None:
    assert len(create_comments()) == 2


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_comment(
    auth: Callable,
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    create_posts()
    comment_input = {
        "commentInput": {
            "title": "test_comment",
            "text": "test_comment_text",
            "post": 1,
        }
    }

    query: str = import_query('createComment.graphql')
    response: Response = client_query(query, comment_input)

    assert response is not None
    assert response.errors is None

    create_comment: Dict = response.data.get('createComment', None)
    assert create_comment is not None

    comment_title: Dict = create_comment.get('title', None)
    assert comment_title is not None
    assert comment_title == "test_comment"

    comment_owner: Dict = create_comment.get('owner', None)
    assert comment_owner is not None
    assert comment_owner.get('username', None) == "jane.doe@blogapp.lo"

    comment_post: Dict = create_comment.get('post', None)
    assert comment_post is not None
    assert comment_post.get('slug', None) == "test_post-1"


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_comment_too_long_fields(
    auth: Callable,
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    create_posts()
    comment_input = {
        "commentInput": {
            "title": "e" * 201,
            "text": "test_comment_text",
            "post": 1,
        }
    }

    query: str = import_query('createComment.graphql')
    response: Response = client_query(query, comment_input)

    assert response is not None
    assert response.errors is None

    create_comment: Dict = response.data.get('createComment', None)
    assert create_comment is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_comment_invalid_post_id(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    comment_input = {
        "commentInput": {
            "title": "test_comment",
            "text": "test_comment_text",
            "post": 1,
        }
    }

    query: str = import_query('createComment.graphql')
    response: Response = client_query(query, comment_input)

    assert response is not None
    assert response.errors is None

    create_comment: Dict = response.data.get('createComment', None)
    assert create_comment is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_comment_invalid_owner_id(
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    comment_input = {
        "commentInput": {
            "title": "test_comment",
            "text": "test_comment_text",
            "post": 1,
        }
    }

    query: str = import_query('createComment.graphql')
    response: Response = client_query(query, comment_input)

    assert response is not None
    assert response.errors is None

    create_comment: Dict = response.data.get('createComment', None)
    assert create_comment is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_update_comment(
    auth: Callable,
    create_comments: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    create_comments()
    comment_input = {
        "commentInput": {
            "id": 2,
            "title": "test_comment3",
            "text": "test_comment_text3",
        }
    }

    query: str = import_query('updateComment.graphql')
    response: Response = client_query(query, comment_input)

    assert response is not None
    assert response.errors is None

    update_comment: Dict = response.data.get('updateComment', None)
    assert update_comment is not None

    comment_title: Dict = update_comment.get('title', None)
    assert comment_title is not None
    assert comment_title == "test_comment3"


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_delete_comment(
    auth: Callable,
    create_comments: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    create_comments()
    comment_input = {"commentId": 2}

    query: str = import_query('deleteComment.graphql')
    response: Response = client_query(query, comment_input)

    assert response is not None
    assert response.errors is None

    delete_comment: Dict = response.data.get('deleteComment', None)
    assert delete_comment is True
