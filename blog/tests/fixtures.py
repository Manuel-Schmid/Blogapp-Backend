import json
import os.path
import re
import typing
from datetime import datetime
from typing import Dict, Optional, Callable, Union, Coroutine, Any

import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.http import JsonResponse
from django.test import Client
from django.utils.timezone import make_aware
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
    AuthorRequest as AuthorRequestType,
    Subscription as SubscriptionType,
    PostRelationType,
)
from blog.models import Category, User, Post, Comment, PostLike, UserStatus, AuthorRequest, PostRelation, Subscription


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
            head, tail = os.path.split(file_path)
            head = os.path.join(head, 'fragments')
            file_path = os.path.join(head, tail)
            if not os.path.exists(file_path):
                raise FileNotFoundError
        with open(file_path) as f:
            file_content = f.read()
            content += file_content

        matches = re.findall('(#import "(.*)")', file_content)
        if len(matches) > 0:
            for import_string, relative_path in matches:
                if relative_path.startswith('./'):
                    relative_path = relative_path[2:]
                content += '\n\n'
                content += read_file(base_path, relative_path, '')
                content = content.replace(import_string, '')
        return content

    def func(path: str) -> str:
        return read_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graphql'), path)

    return func


@pytest.fixture(name='query_post')
def fixture_query_post(
    create_categories: Callable,
) -> Callable:
    def func(query: str, post_input: Dict, image: Union[SimpleUploadedFile]) -> Dict:
        create_categories()

        query = query
        data = {
            'operations': json.dumps(
                {
                    'query': query,
                    'variables': {
                        'postInput': post_input,
                    },
                }
            ),
            '1': image,
            'map': json.dumps(
                {
                    '1': ['variables.postInput.image'],
                }
            ),
        }

        response = graphql_client.client.post('/graphql/', data=data)
        json_data: Dict = json.loads(response.content)
        return json_data

    return func


@pytest.fixture(name='query_user_registration')
def fixture_query_user_registration() -> Callable:
    def func(query: str, user_registration_input: Dict, avatar: Union[SimpleUploadedFile]) -> Dict:

        query = query
        data = {
            'operations': json.dumps(
                {
                    'query': query,
                    'variables': {
                        'userRegistrationInput': user_registration_input,
                    },
                }
            ),
            '1': avatar,
            'map': json.dumps(
                {
                    '1': ['variables.userRegistrationInput.avatar'],
                }
            ),
        }

        response = graphql_client.client.post('/graphql/', data=data)
        json_data: Dict = json.loads(response.content)
        return json_data

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
    def func(is_author: bool = True) -> None:
        username: str = 'jane.doe@blogapp.lo'
        password: str = 'admin_password_155'
        user: User = create_user(username=username, is_superuser=True)
        user.set_password(password)
        user.save()
        UserStatus.objects.create(
            user=user,
            verified=True,
            archived=False,
            secondary_email=False,
            is_author=is_author,
        )
        return login(username, password)

    return func


@pytest.fixture(name='get_token_from_mail')
def fixture_get_token_from_mail() -> Callable:
    def func(mail_body: any, path: str) -> str:
        regex = r'{}://{}:{}/{}/(.+)\"'.format(
            re.escape(settings.FRONTEND_PROTOCOL),
            re.escape(settings.FRONTEND_DOMAIN),
            re.escape(settings.FRONTEND_PORT),
            re.escape(path),
        )
        url = re.findall(regex, str(mail_body))
        return url[0] if len(url) > 0 else None

    return func


@pytest.fixture(name='file_image_jpg')
def file_image_jpg() -> SimpleUploadedFile:
    mime_type = 'image/jpeg'
    image_path = os.path.join(settings.BASE_DIR, 'blog', 'tests', 'media', 'image.jpg')
    file = open(image_path, 'rb').read()
    return SimpleUploadedFile(name='image.jpg', content=file, content_type=mime_type)


@pytest.fixture(name='file_image_png')
def file_image_png() -> SimpleUploadedFile:
    mime_type = 'image/png'
    image_path = os.path.join(settings.BASE_DIR, 'blog', 'tests', 'media', 'image.png')
    file = open(image_path, 'rb').read()
    return SimpleUploadedFile(name='image.png', content=file, content_type=mime_type)


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
    def func(assert_errors: bool = True) -> JsonResponse:
        mutation: str = import_query('deleteTokenCookie.graphql')
        response = graphql_client.raw_query(mutation, None, asserts_errors=False)

        if assert_errors:
            cookies: Dict = response.cookies
            assert cookies is not None
            assert jwt_settings.JWT_COOKIE_NAME in cookies
            assert cookies[jwt_settings.JWT_COOKIE_NAME].value == ''
            assert jwt_settings.JWT_REFRESH_TOKEN_COOKIE_NAME in cookies
            assert cookies[jwt_settings.JWT_REFRESH_TOKEN_COOKIE_NAME].value == ''

        graphql_client.logout()
        return response

    return func


@pytest.fixture(name='auto_logout', autouse=True)
def fixture_auto_logout(logout: Callable) -> None:
    # automatically logout before each test
    logout(assert_errors=False)


@pytest.fixture(name='create_users')
def fixture_create_users(client_query: Callable, import_query: Callable) -> Callable:
    def func() -> typing.List[UserType]:
        user1 = User.objects.create(username='test_user1', email='user1@example.com')
        user1.set_password('password1')
        user1.save()
        UserStatus.objects.create(user=user1, verified=True, archived=False, secondary_email=False)
        user2 = User.objects.create(username='test_user2', email='user2@example.com')
        user2.set_password('password2')
        user2.save()
        UserStatus.objects.create(user=user2, verified=True, is_author=True, archived=False, secondary_email=False)
        return User.objects.all()

    return func


@pytest.fixture(name='create_categories')
def fixture_create_categories(client_query: Callable, import_query: Callable) -> Callable:
    def func() -> typing.List[CategoryType]:
        Category.objects.create(name='test_category1', slug='test_category1')
        Category.objects.create(name='test_category2', slug='test_category2')
        return Category.objects.all()

    return func


@pytest.fixture(name='create_author_requests')
def fixture_create_author_requests(create_users: Callable, client_query: Callable, import_query: Callable) -> Callable:
    def func() -> typing.List[AuthorRequestType]:
        users = create_users()
        AuthorRequest.objects.create(
            date_opened=make_aware(datetime(2022, 12, 1, 12, 00, 00, 000000)),
            date_closed=make_aware(datetime(2022, 12, 1, 14, 30, 00, 000000)),
            status='REJECTED',
            user_id=users[0].id,
        )
        AuthorRequest.objects.create(
            date_opened=make_aware(datetime(2022, 12, 1, 13, 00, 00, 000000)), status='PENDING', user_id=users[1].id
        )
        return AuthorRequest.objects.all()

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
            title='Test_Post 1', text='test_text1', owner=users[0], category=categories[0], status='PUBLISHED'
        )
        Post.objects.create(
            title='Test_Post 2', text='test_text2', owner=users[1], category=categories[1], status='PUBLISHED'
        )
        Post.objects.create(
            title='Test_Post 3', text='test_text3', owner=users[1], category=categories[0], status='DRAFT'
        )
        return Post.objects.all()

    return func


@pytest.fixture(name='create_posts_with_relations')
def fixture_create_posts_with_relations(
    create_posts: Callable,
    client_query: Callable,
    import_query: Callable,
) -> Callable:
    def func() -> typing.List[PostRelationType]:
        posts = create_posts()
        users = User.objects.all()
        PostRelation.objects.create(main_post=posts[0], sub_post=posts[1], creator=users[0])
        PostRelation.objects.create(main_post=posts[1], sub_post=posts[2], creator=users[1])
        PostRelation.objects.create(main_post=posts[2], sub_post=posts[1], creator=users[1])
        return PostRelation.objects.all()

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


@pytest.fixture(name='create_subscription')
def fixture_create_subscription(
    create_users: Callable,
    client_query: Callable,
    import_query: Callable,
) -> Callable:
    def func() -> typing.List[SubscriptionType]:
        users = create_users()
        Subscription.objects.create(
            subscriber=users[0], author=users[1], date_created=datetime(2023, 3, 22, 00, 00, 00, 000000)
        )
        return Subscription.objects.all()

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
        TaggedItem.objects.create(tag=tag1, object_id=posts[0].id, content_type=content_type)
        tag2 = Tag.objects.create(name='tag_2', slug='tag_2_slug')
        TaggedItem.objects.create(tag=tag2, object_id=posts[1].id, content_type=content_type)
        Tag.objects.create(name='tag_3', slug='tag_3_slug')
        return Tag.objects.all()

    return func
