from typing import Callable, Dict
import pytest
from strawberry.test import Response


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_all_posts(
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()

    query: str = import_query('paginatedFilteredPostsQuery.graphql')
    response: Response = client_query(query)

    assert response is not None
    assert response.errors is None

    paginated_posts: Dict = response.data.get('paginatedPosts', None)
    assert paginated_posts is not None

    num_post_pages: Dict = paginated_posts.get('numPostPages', None)
    assert num_post_pages is not None
    assert num_post_pages == 1

    posts: Dict = paginated_posts.get('posts', None)
    assert posts is not None
    assert len(posts) == 2
    post1_title = posts[0].get('title', None)
    assert post1_title is not None
    assert post1_title == 'Test_Post 1'
    post2_title = posts[1].get('title', None)
    assert post2_title is not None
    assert post2_title == 'Test_Post 2'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_posts_by_category(
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    filter_input = {
        "categorySlug": "test_category1",
    }

    query: str = import_query('paginatedFilteredPostsQuery.graphql')
    response: Response = client_query(query, filter_input)

    assert response is not None
    assert response.errors is None

    paginated_posts: Dict = response.data.get('paginatedPosts', None)
    assert paginated_posts is not None

    num_post_pages: Dict = paginated_posts.get('numPostPages', None)
    assert num_post_pages is not None
    assert num_post_pages == 1

    posts: Dict = paginated_posts.get('posts', None)
    assert posts is not None
    assert len(posts) == 1
    post1_title = posts[0].get('title', None)
    assert post1_title is not None
    assert post1_title == 'Test_Post 1'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_posts_by_tag(
    create_tags: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_tags()
    filter_input = {
        "tagSlugs": "tag_2_slug",
    }

    query: str = import_query('paginatedFilteredPostsQuery.graphql')
    response: Response = client_query(query, filter_input)

    assert response is not None
    assert response.errors is None

    paginated_posts: Dict = response.data.get('paginatedPosts', None)
    assert paginated_posts is not None

    num_post_pages: Dict = paginated_posts.get('numPostPages', None)
    assert num_post_pages is not None
    assert num_post_pages == 1

    posts: Dict = paginated_posts.get('posts', None)
    assert posts is not None
    assert len(posts) == 1
    post1_title = posts[0].get('title', None)
    assert post1_title is not None
    assert post1_title == 'Test_Post 2'
