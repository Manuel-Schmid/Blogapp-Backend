import json
import os.path
import re
import typing
from typing import Dict, Optional, Callable, Union, Coroutine, Any

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import JsonResponse
from django.test import Client
from strawberry.test import BaseGraphQLTestClient, Response
from strawberry_django_jwt.settings import jwt_settings
from taggit.models import Tag, TaggedItem

from blog.api.types import (
    Category as CategoryType,
    User as UserType,
    Tag as TagType,
    Post as PostType,
    Comment as CommentType,
    PostLike as PostLikeType,
)
from blog.models import Category, User, Post, Comment, PostLike


class GraphqlTestClient(BaseGraphQLTestClient):
    def __init__(self, client: Client, path: str) -> None:
        super().__init__(client)
        self.client = client
        self.path = path

    def raw_query(
        self,
        query: str,
        variables: Optional[Dict[str, object]] = None,
        headers: Optional[Dict[str, object]] = None,
        asserts_errors: Optional[bool] = True,
        files: Optional[Dict[str, object]] = None,
    ) -> Union[Coroutine[Any, Any, Response], Response, JsonResponse]:
        body = self._build_body(query, variables, files)

        return self.request(body, headers, files)

    def request(
        self,
        body: Dict[str, object],
        headers: Optional[Dict[str, object]] = None,
        files: Optional[Dict[str, object]] = None,
    ) -> Response:
        kwargs: Dict[str, object] = {'data': body}
        if files:  # pragma:nocover
            kwargs['format'] = 'multipart'
        else:
            kwargs['content_type'] = 'application/json'
        return self.client.post(self.path, **kwargs)

    def login(self, **credentials: Dict[str, object]) -> None:
        self.client.login(**credentials)

    def logout(self) -> None:
        self.client.logout()


_client = Client()
graphql_client = GraphqlTestClient(_client, '/graphql/')


@pytest.fixture(name='client_query')
def client_query() -> Callable:
    def func(
        query: str,
        variables: Optional[Dict[str, object]] = None,
        raw_response: bool = False,
    ) -> Union[Response, JsonResponse]:
        if raw_response:
            return graphql_client.raw_query(query, variables, asserts_errors=False)
        return graphql_client.query(query, variables, asserts_errors=False)

    return func


@pytest.fixture(name='import_query')
def import_query() -> Callable:
    def read_file(base_path: str, path: str, content: str = '') -> str:
        file_path = os.path.join(base_path, path)
        if not os.path.exists(file_path):
            raise FileNotFoundError
        with open(file_path) as f:
            file_content = f.read()
            content += file_content

        matches = re.findall("(#import \"(.*)\")", file_content)
        if len(matches) > 0:
            for import_string, relative_path in matches:
                if relative_path.startswith('./'):
                    relative_path = relative_path[2:]
                content += "\n\n"
                content += read_file(base_path, relative_path, '')
                content = content.replace(import_string, '')
        return content

    def func(path: str) -> str:
        return read_file(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graphql'), path
        )

    return func


@pytest.fixture(name='create_user')
def fixture_create_user(django_user_model: models.Model) -> Callable:
    def func(**kwargs) -> models.Model:
        return django_user_model.objects.create_user(**kwargs)

    return func


@pytest.fixture(name='auth')
def fixture_auth(
    create_user: Callable,
    login: Callable,
    client_query: Callable,
    import_query: Callable,
) -> Callable:
    def func() -> None:
        username: str = 'jane.doe@blogapp.lo'
        password: str = 'admin_password_155'
        user: User = create_user(username=username)
        user.set_password(password)
        user.save()
        return login(username, password)

    return func


@pytest.fixture(name='login')
def fixture_login(client_query: Callable, import_query: Callable) -> Callable:
    def func(username: str, password: str) -> JsonResponse:
        credentials = {'username': username, 'password': password}
        mutation: str = import_query('tokenAuth.graphql')
        response = graphql_client.raw_query(mutation, credentials, asserts_errors=False)

        cookies: Dict = response.cookies
        assert cookies is not None
        assert jwt_settings.JWT_COOKIE_NAME in cookies
        assert jwt_settings.JWT_REFRESH_TOKEN_COOKIE_NAME in cookies

        json_data: Dict = json.loads(response.content)
        assert json_data.get('errors', None) is None

        data: Dict = json_data.get('data', None)
        assert data is not None

        token_auth: Optional[Dict] = data.get('tokenAuth', None)
        assert token_auth is not None
        assert token_auth.get('token') is not None
        assert token_auth.get('refreshToken') is not None
        assert token_auth.get('refreshExpiresIn') is not None

        payload: Optional[Dict] = token_auth.get('payload', None)
        assert payload is not None
        assert payload.get('username', None) == username
        graphql_client.login(**credentials)
        return response

    return func


@pytest.fixture(name='logout')
def fixture_logout(client_query: Callable, import_query: Callable) -> Callable:
    def func() -> JsonResponse:
        mutation: str = import_query('deleteTokenCookie.graphql')
        response = graphql_client.raw_query(mutation, None, asserts_errors=False)

        cookies: Dict = response.cookies

        assert cookies is not None
        assert jwt_settings.JWT_COOKIE_NAME in cookies
        assert cookies[jwt_settings.JWT_COOKIE_NAME].value == ''
        assert jwt_settings.JWT_REFRESH_TOKEN_COOKIE_NAME in cookies
        assert cookies[jwt_settings.JWT_REFRESH_TOKEN_COOKIE_NAME].value == ''
        graphql_client.logout()
        return response

    return func


@pytest.fixture(name='create_users')
def fixture_create_users(client_query: Callable, import_query: Callable) -> Callable:
    def func() -> typing.List[UserType]:
        user1 = User.objects.create(username='test_user1', email='user1@example.com')
        user1.set_password('password1')
        user1.save()
        user2 = User.objects.create(username='test_user2', email='user2@example.com')
        user2.set_password('password2')
        user2.save()
        return User.objects.all()

    return func


@pytest.fixture(name='create_categories')
def fixture_create_categories(
    client_query: Callable, import_query: Callable
) -> Callable:
    def func() -> typing.List[CategoryType]:
        Category.objects.create(name='test_category1', slug='test_category1')
        Category.objects.create(name='test_category2', slug='test_category2')
        return Category.objects.all()

    return func


@pytest.fixture(name='create_posts')
def fixture_create_posts(
    create_users: Callable,
    create_categories: Callable,
    client_query: Callable,
    import_query: Callable,
) -> Callable:
    def func() -> typing.List[PostType]:
        users = create_users()
        categories = create_categories()
        Post.objects.create(
            title='Test_Post 1',
            text='test_text1',
            owner=users[0],
            category=categories[0],
        )
        Post.objects.create(
            title='Test_Post 2',
            text='test_text2',
            owner=users[1],
            category=categories[1],
        )
        return Post.objects.all()

    return func


@pytest.fixture(name='create_comments')
def fixture_create_comments(
    create_posts: Callable,
    client_query: Callable,
    import_query: Callable,
) -> Callable:
    def func() -> typing.List[CommentType]:
        posts = create_posts()
        users = User.objects.all()
        Comment.objects.create(title='test_comment1', post=posts[0], owner=users[0])
        Comment.objects.create(title='test_comment2', post=posts[1], owner=users[1])
        return Comment.objects.all()

    return func


@pytest.fixture(name='create_post_likes')
def fixture_create_post_likes(
    create_posts: Callable,
    client_query: Callable,
    import_query: Callable,
) -> Callable:
    def func() -> typing.List[PostLikeType]:
        posts = create_posts()
        users = User.objects.all()
        PostLike.objects.create(user=users[0], post=posts[1])
        PostLike.objects.create(user=users[1], post=posts[1])
        return PostLike.objects.all()

    return func


@pytest.fixture(name='create_tags')
def fixture_create_tags(
    create_posts: Callable,
    client_query: Callable,
    import_query: Callable,
) -> Callable:
    def func() -> typing.List[TagType]:
        posts = create_posts()
        content_type = ContentType.objects.get(app_label='blog', model='post')
        tag1 = Tag.objects.create(name='tag_1', slug='tag_1_slug')
        TaggedItem.objects.create(
            tag=tag1, object_id=posts[0].id, content_type=content_type
        )
        tag2 = Tag.objects.create(name='tag_2', slug='tag_2_slug')
        TaggedItem.objects.create(
            tag=tag2, object_id=posts[1].id, content_type=content_type
        )
        Tag.objects.create(name='tag_3', slug='tag_3_slug')
        return Tag.objects.all()

    return func
