from typing import Callable, Dict
import pytest
from strawberry.test import Response


@pytest.mark.django_db
def test_create_post_likes(
    create_post_likes: Callable, import_query: Callable, client_query: Callable
) -> None:
    assert len(create_post_likes()) == 2


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_and_delete_post_like(
    auth: Callable,
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()
    create_posts()
    post_like_input = {
        'postLikeInput': {
            'post': 1,
        }
    }

    query: str = import_query('createPostLike.graphql')
    response: Response = client_query(query, post_like_input)

    assert response is not None
    assert response.errors is None

    create_post_like: Dict = response.data.get('createPostLike', None)
    assert create_post_like is not None

    post_like_id: Dict = create_post_like.get('id', None)
    assert post_like_id is not None
    assert post_like_id == '1'

    post_like_user: Dict = create_post_like.get('user', None)
    assert post_like_user is not None
    assert post_like_user.get('username', None) == 'jane.doe@blogapp.lo'

    post_like_post: Dict = create_post_like.get('post', None)
    assert post_like_post is not None
    assert post_like_post.get('id', None) == '1'
    assert post_like_post.get('likeCount', None) == 1

    query: str = import_query('deletePostLike.graphql')
    response: Response = client_query(query, post_like_input)

    assert response is not None
    assert response.errors is None

    delete_post_like: Dict = response.data.get('deletePostLike', None)
    assert delete_post_like is True
