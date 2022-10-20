import json
import os.path
import re
from typing import Dict, Optional, Callable, Union, Coroutine, Any

import pytest
from django.db import models
from django.http import JsonResponse
from django.test import Client
from strawberry.test import BaseGraphQLTestClient, Response
from strawberry_django_jwt.settings import jwt_settings

from blog.models import Category


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


@pytest.fixture(name='create_categories')
def fixture_create_categories(
    client_query: Callable, import_query: Callable
) -> Callable:
    def func() -> JsonResponse:
        category_input = {
            "categoryInput": {
                "name": "test_category",
            }
        }
        mutation: str = import_query('createCategory.graphql')
        graphql_client.raw_query(mutation, category_input, asserts_errors=False)
        response = graphql_client.raw_query(
            mutation, category_input, asserts_errors=False
        )

        json_data: Dict = json.loads(response.content)
        assert json_data.get('errors', None) is None

        data: Dict = json_data.get('data', None)
        assert data is not None

        create_category: Dict = data.get('createCategory', None)
        assert create_category is not None

        category_id: Dict = create_category.get('id', None)
        assert category_id is not None
        assert category_id == "2"

        return response

    return func
