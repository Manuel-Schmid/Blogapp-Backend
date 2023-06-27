from blog.models import Notification
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
        'categorySlug': 'test_category1',
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
        'tagSlugs': 'tag_2_slug',
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


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_existing_post_by_tag_and_category(
    create_tags: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_tags()
    filter_input = {'tagSlugs': 'tag_2_slug', 'categorySlug': 'test_category2'}

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


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_non_existent_post_by_tag_and_category(
    create_tags: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_tags()
    filter_input = {'tagSlugs': 'tag_2_slug', 'categorySlug': 'test_category1'}

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
    assert len(posts) == 0


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_notification_posts(
    create_posts: Callable,
    login: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    posts = create_posts()
    Notification.objects.create(user_id=1, post=posts[1])
    Notification.objects.create(user_id=1, post=posts[2])

    login('test_user1', 'password1')

    notification_posts_input = {'activePage': 1}
    query: str = import_query('getNotificationPosts.graphql')
    response: Response = client_query(query, notification_posts_input)

    assert response is not None
    assert response.errors is None

    paginated_posts: Dict = response.data.get('paginatedNotificationPosts', None)
    assert paginated_posts is not None

    num_post_pages: Dict = paginated_posts.get('numPostPages', None)
    assert num_post_pages is not None
    assert num_post_pages == 1

    posts: Dict = paginated_posts.get('posts', None)
    assert posts is not None
    assert len(posts) == 1
    assert posts[0].get('slug', None) == 'test_post-2'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_notification_posts_empty_page(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()

    notification_posts_input = {'activePage': 5}
    query: str = import_query('getNotificationPosts.graphql')
    response: Response = client_query(query, notification_posts_input)

    assert response is not None
    assert response.data is None
    assert response.errors is not None

    assert len(response.errors) > 0
    error: Dict = response.errors[0]
    assert error.get('message', None) == 'That page contains no results'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_user_posts(
    create_posts: Callable,
    login: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    login('test_user1', 'password1')
    user_posts_input = {'activePage': 1}

    query: str = import_query('getUserPosts.graphql')
    response: Response = client_query(query, user_posts_input)

    assert response is not None
    assert response.errors is None

    paginated_posts: Dict = response.data.get('paginatedUserPosts', None)
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
def test_query_user_posts_unauthenticated(
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    user_posts_input = {'activePage': 1}

    query: str = import_query('getUserPosts.graphql')
    response: Dict = client_query(query, user_posts_input)

    assert response is not None
    data = response.data
    assert data is None
    response_errors = response.errors
    assert response_errors is not None

    assert len(response_errors) > 0
    error: Dict = response_errors[0]
    extensions = error.get('extensions', None)
    code = extensions.get('code', None)
    assert code is not None
    assert code == 'PERMISSION_DENIED'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_published_post_by_slug(
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    post_slug = {'slug': 'test_post-1'}

    query: str = import_query('getPostBySlug.graphql')
    response: Dict = client_query(query, post_slug)

    assert response is not None
    assert response.errors is None

    post_by_slug: Dict = response.data.get('postBySlug', None)
    assert post_by_slug is not None
    post: Dict = post_by_slug.get('post', None)
    assert post is not None

    post_title = post.get('title', None)
    assert post_title is not None
    assert post_title == 'Test_Post 1'

    post_status = post.get('status', None)
    assert post_status is not None
    assert post_status == 'PUBLISHED'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_draft_post_by_slug(
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    post_slug = {'slug': 'test_post-3'}

    query: str = import_query('getPostBySlug.graphql')
    response: Dict = client_query(query, post_slug)

    assert response is not None
    assert response.errors is None

    postBySlug: Dict = response.data.get('postBySlug', None)
    assert postBySlug is not None
    success: Dict = postBySlug.get('success', None)
    assert success is False
    errors: Dict = postBySlug.get('errors', None)
    assert errors is not None
    assert 'post' in errors


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_draft_post_by_slug_not_owner(
    create_posts: Callable,
    login: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    login('test_user1', 'password1')
    post_slug = {'slug': 'test_post-3'}

    query: str = import_query('getPostBySlug.graphql')
    response: Dict = client_query(query, post_slug)

    assert response is not None
    assert response.errors is None

    postBySlug: Dict = response.data.get('postBySlug', None)
    assert postBySlug is not None
    success: Dict = postBySlug.get('success', None)
    assert success is False
    errors: Dict = postBySlug.get('errors', None)
    assert errors is not None
    assert 'post' in errors


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_query_draft_post_by_slug_owner(
    create_posts: Callable,
    login: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    login('test_user2', 'password2')
    post_slug = {'slug': 'test_post-3'}

    query: str = import_query('getPostBySlug.graphql')
    response: Dict = client_query(query, post_slug)

    assert response is not None
    assert response.errors is None

    post_by_slug: Dict = response.data.get('postBySlug', None)
    assert post_by_slug is not None
    post: Dict = post_by_slug.get('post', None)
    assert post is not None

    post_title = post.get('title', None)
    assert post_title is not None
    assert post_title == 'Test_Post 3'

    post_status = post.get('status', None)
    assert post_status is not None
    assert post_status == 'DRAFT'
