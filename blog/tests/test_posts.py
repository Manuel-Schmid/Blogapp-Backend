from typing import Callable, Dict
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from strawberry.test import Response


@pytest.mark.django_db
def test_create_posts(create_posts: Callable) -> None:
    assert len(create_posts()) == 3


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_post_with_relations(
    auth: Callable,
    create_posts_with_relations: Callable,
    import_query: Callable,
    query_post: Callable,
    file_image_jpg: SimpleUploadedFile,
) -> None:
    auth()
    create_posts_with_relations()
    post_input = {'title': 'test_post', 'text': 'this a test', 'category': 2, 'relatedPosts': [1, 2]}

    query: str = import_query('createPost.graphql')
    response: Dict = query_post(query, post_input, file_image_jpg)

    assert response is not None
    response_errors = response.get('errors', None)
    assert response_errors is None
    data = response.get('data', None)
    assert data is not None

    create_post: Dict = data.get('createPost', None)
    assert create_post is not None

    success: Dict = create_post.get('success', None)
    assert success is True
    errors: Dict = create_post.get('errors', None)
    assert errors is None
    post: Dict = create_post.get('post', None)
    assert post is not None

    post_title: Dict = post.get('title', None)
    assert post_title is not None
    assert post_title == 'test_post'

    post_slug: Dict = post.get('slug', None)
    assert post_slug is not None
    assert post_slug == 'test_post'

    post_image: Dict = post.get('image', None)
    assert post_image is not None

    post_owner: Dict = post.get('owner', None)
    assert post_owner is not None
    assert post_owner.get('username', None) == 'jane.doe@blogapp.lo'

    post_category: Dict = post.get('category', None)
    assert post_category is not None
    assert post_category.get('slug', None) == 'test_category2'

    related_sub_posts: Dict = post.get('relatedSubPosts', None)
    assert related_sub_posts is not None
    assert len(related_sub_posts) > 0
    assert related_sub_posts[0].get('id', None) == '1'
    assert related_sub_posts[1].get('id', None) == '2'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_post_not_an_author(
    auth: Callable,
    import_query: Callable,
    query_post: Callable,
    file_image_jpg: SimpleUploadedFile,
) -> None:
    auth(is_author=False)
    post_input = {
        'title': 'test_post',
        'text': 'this a test',
        'category': 1,
    }

    query: str = import_query('createPost.graphql')
    response: Dict = query_post(query, post_input, file_image_jpg)

    assert response is not None
    data = response.get('data', None)
    assert data is None
    response_errors = response.get('errors', None)
    assert response_errors is not None

    assert len(response_errors) > 0
    error: Dict = response_errors[0]
    extensions = error.get('extensions', None)
    code = extensions.get('code', None)
    assert code is not None
    assert code == 'PERMISSION_DENIED'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_post_too_long_fields(
    auth: Callable,
    import_query: Callable,
    query_post: Callable,
    file_image_jpg: SimpleUploadedFile,
) -> None:
    auth()
    post_input = {
        'title': 'e' * 201,
        'text': 'this a test',
        'category': 2,
    }

    query: str = import_query('createPost.graphql')
    response: Dict = query_post(query, post_input, file_image_jpg)

    assert response is not None
    response_errors = response.get('errors', None)
    assert response_errors is None
    data = response.get('data', None)
    assert data is not None

    create_post: Dict = data.get('createPost', None)
    assert create_post is not None

    errors: Dict = create_post.get('errors', None)
    assert errors is not None
    title_error = errors.get('title', None)
    assert title_error[0].get('code', None) == 'max_length'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_post_invalid_owner_id(
    import_query: Callable,
    query_post: Callable,
    file_image_jpg: SimpleUploadedFile,
) -> None:
    post_input = {
        'title': 'test_post',
        'text': 'this a test',
        'category': 2,
    }

    query: str = import_query('createPost.graphql')
    response: Dict = query_post(query, post_input, file_image_jpg)

    assert response is not None
    data = response.get('data', None)
    assert data is None
    response_errors = response.get('errors', None)
    assert response_errors is not None

    assert len(response_errors) > 0
    error: Dict = response_errors[0]
    extensions = error.get('extensions', None)
    code = extensions.get('code', None)
    assert code is not None
    assert code == 'PERMISSION_DENIED'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_create_post_invalid_category_id(
    auth: Callable,
    import_query: Callable,
    query_post: Callable,
    file_image_jpg: SimpleUploadedFile,
) -> None:
    auth()
    post_input = {
        'title': 'test_post',
        'text': 'this a test',
        'category': 3,
    }

    query: str = import_query('createPost.graphql')
    response: Dict = query_post(query, post_input, file_image_jpg)

    assert response is not None
    response_errors = response.get('errors', None)
    assert response_errors is None
    data = response.get('data', None)
    assert data is not None

    create_post: Dict = data.get('createPost', None)
    assert create_post is not None

    errors: Dict = create_post.get('errors', None)
    assert errors is not None
    category_error = errors.get('category', None)
    assert category_error[0].get('code', None) == 'invalid_choice'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_update_post_with_image(
    create_posts_with_relations: Callable,
    login: Callable,
    import_query: Callable,
    query_post: Callable,
    file_image_png: SimpleUploadedFile,
) -> None:
    create_posts_with_relations()
    login('test_user2', 'password2')
    post_input = {
        'slug': 'test_post-2',
        'title': 'Test_post3',
        'text': 'New Text',
        'category': 1,
        'owner': 1,
        'relatedPosts': [1],
    }

    query: str = import_query('updatePost.graphql')
    response: Dict = query_post(query, post_input, file_image_png)

    assert response is not None
    response_errors = response.get('errors', None)
    assert response_errors is None
    data = response.get('data', None)
    assert data is not None

    update_post: Dict = data.get('updatePost', None)
    assert update_post is not None

    success: Dict = update_post.get('success', None)
    assert success is True
    errors: Dict = update_post.get('errors', None)
    assert errors is None
    post: Dict = update_post.get('post', None)
    assert post is not None

    post_title: Dict = post.get('title', None)
    assert post_title is not None
    assert post_title == 'Test_post3'

    post_slug: Dict = post.get('slug', None)
    assert post_slug is not None
    assert post_slug == 'test_post-2'

    post_image: Dict = post.get('image', None)
    assert post_image is not None

    post_owner: Dict = post.get('owner', None)
    assert post_owner is not None
    assert post_owner.get('username', None) == 'test_user1'

    post_category: Dict = post.get('category', None)
    assert post_category is not None
    assert post_category.get('slug', None) == 'test_category1'

    related_sub_posts: Dict = post.get('relatedSubPosts', None)
    assert related_sub_posts is not None
    assert len(related_sub_posts) > 0
    assert related_sub_posts[0].get('id', None) == '1'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_update_post_without_image(
    create_posts_with_relations: Callable,
    login: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts_with_relations()
    login('test_user2', 'password2')
    post_input = {
        'postInput': {
            'slug': 'test_post-2',
            'title': 'Test_post3',
            'text': 'New Text',
            'category': 1,
            'owner': 1,
            'relatedPosts': [1, 3],
        }
    }

    query: str = import_query('updatePost.graphql')
    response: Response = client_query(query, post_input)

    assert response is not None
    assert response.errors is None

    update_post: Dict = response.data.get('updatePost', None)
    assert update_post is not None

    success: Dict = update_post.get('success', None)
    assert success is True
    errors: Dict = update_post.get('errors', None)
    assert errors is None
    post: Dict = update_post.get('post', None)
    assert post is not None

    post_title: Dict = post.get('title', None)
    assert post_title is not None
    assert post_title == 'Test_post3'

    post_slug: Dict = post.get('slug', None)
    assert post_slug is not None
    assert post_slug == 'test_post-2'

    post_owner: Dict = post.get('owner', None)
    assert post_owner is not None
    assert post_owner.get('username', None) == 'test_user1'

    post_category: Dict = post.get('category', None)
    assert post_category is not None
    assert post_category.get('slug', None) == 'test_category1'

    related_sub_posts: Dict = post.get('relatedSubPosts', None)
    assert related_sub_posts is not None
    assert len(related_sub_posts) > 0
    assert related_sub_posts[0].get('id', None) == '1'
    assert related_sub_posts[1].get('id', None) == '3'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_update_post_status(
    create_posts: Callable,
    login: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    login('test_user2', 'password2')

    update_post_status_input = {
        'updatePostStatusInput': {
            'postSlug': 'test_post-3',
            'status': 'PUBLISHED',
        }
    }

    query: str = import_query('updatePostStatus.graphql')
    response: Response = client_query(query, update_post_status_input)

    assert response is not None
    assert response.errors is None

    update_post_status: Dict = response.data.get('updatePostStatus', None)
    assert update_post_status is not None

    success: Dict = update_post_status.get('success', None)
    assert success is not None
    assert success is True
    errors: Dict = update_post_status.get('errors', None)
    assert errors is None

    post: Dict = update_post_status.get('post', None)
    assert post is not None

    post_title = post.get('title', None)
    assert post_title is not None
    assert post_title == 'Test_Post 3'

    post_status = post.get('status', None)
    assert post_status is not None
    assert post_status == 'PUBLISHED'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_update_post_status_unauthenticated(
    create_posts: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()

    update_post_status_input = {
        'updatePostStatusInput': {
            'postSlug': 'test_post-3',
            'status': 'PUBLISHED',
        }
    }

    query: str = import_query('updatePostStatus.graphql')
    response: Response = client_query(query, update_post_status_input)

    assert response is not None
    assert response.data is None
    assert response.errors is not None
    assert len(response.errors) > 0
    error: Dict = response.errors[0]
    extensions = error.get('extensions', None)
    code = extensions.get('code', None)
    assert code is not None
    assert code == 'PERMISSION_DENIED'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_update_post_status_no_author(
    create_posts: Callable,
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    auth(is_author=False)

    update_post_status_input = {
        'updatePostStatusInput': {
            'postSlug': 'test_post-3',
            'status': 'PUBLISHED',
        }
    }

    query: str = import_query('updatePostStatus.graphql')
    response: Response = client_query(query, update_post_status_input)

    assert response is not None
    assert response.data is None
    assert response.errors is not None
    assert len(response.errors) > 0
    error: Dict = response.errors[0]
    extensions = error.get('extensions', None)
    code = extensions.get('code', None)
    assert code is not None
    assert code == 'PERMISSION_DENIED'


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_update_post_status_not_post_owner(
    create_posts: Callable,
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_posts()
    auth(is_author=True)

    update_post_status_input = {
        'updatePostStatusInput': {
            'postSlug': 'test_post-3',
            'status': 'PUBLISHED',
        }
    }

    query: str = import_query('updatePostStatus.graphql')
    response: Response = client_query(query, update_post_status_input)

    assert response is not None
    assert response.errors is None

    update_post_status: Dict = response.data.get('updatePostStatus', None)
    assert update_post_status is not None

    success: Dict = update_post_status.get('success', None)
    assert success is not None
    assert success is False
    errors: Dict = update_post_status.get('errors', None)
    assert errors is not None
    error_msg = errors.get('message', None)
    assert error_msg is not None
    assert error_msg == 'You are only allowed to update the status of your own posts'
