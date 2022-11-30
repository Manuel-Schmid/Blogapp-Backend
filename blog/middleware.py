from datetime import datetime
from http.client import HTTPResponse
from typing import Callable, Union

from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from django.utils.functional import SimpleLazyObject
from strawberry_django_jwt.exceptions import JSONWebTokenError
from strawberry_django_jwt.refresh_token.shortcuts import create_refresh_token
from strawberry_django_jwt.settings import jwt_settings
from strawberry_django_jwt.shortcuts import get_user_by_token, get_token
from strawberry_django_jwt.utils import get_credentials, delete_cookie

from blog.models import User


class JWTAuthenticationMiddleware:
    """
    Middleware that ensures that a user can log in via graphql and django admin
    """

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: WSGIRequest) -> HTTPResponse:
        request.user = SimpleLazyObject(lambda: self.__class__.get_jwt_user(request))
        response = self.get_response(request)

        # flag set by deleteTokenCookie mutation
        delete_jwt_cookie = getattr(request, 'delete_jwt_cookie', False)

        # ensure jwt cookie is set if user has logged in via admin
        if request.user and request.user.is_authenticated and not delete_jwt_cookie:
            token = get_token(request.user)
            if token:
                expires = datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA
                response.set_cookie(
                    jwt_settings.JWT_COOKIE_NAME,
                    token,
                    expires=expires,
                    httponly=True,
                    secure=jwt_settings.JWT_COOKIE_SECURE,
                )

                refresh_token = create_refresh_token(request.user)
                expires = refresh_token.created + jwt_settings.JWT_REFRESH_EXPIRATION_DELTA

                response.set_cookie(
                    jwt_settings.JWT_REFRESH_TOKEN_COOKIE_NAME,
                    refresh_token.token,
                    expires=expires,
                    httponly=True,
                    secure=jwt_settings.JWT_COOKIE_SECURE,
                )

        # ensure cookies are deleted
        # jwt cookie needs to be deleted if user has logged out via admin
        # session cookie needs to be deleted if user has logged out via deleteTokenCookie mutation
        if request.path == reverse('admin:logout') or delete_jwt_cookie:
            delete_cookie(response, jwt_settings.JWT_COOKIE_NAME)
            delete_cookie(response, jwt_settings.JWT_REFRESH_TOKEN_COOKIE_NAME)
            delete_cookie(response, settings.SESSION_COOKIE_NAME)
        return response

    @staticmethod
    def get_jwt_user(request: WSGIRequest, **kwargs) -> Union[User, AnonymousUser]:
        user = get_user(request)
        if user.is_authenticated:
            return user
        token = get_credentials(request, **kwargs)
        try:
            if token is not None:
                user = get_user_by_token(token, request)
                if user is not None:
                    return user
        except JSONWebTokenError:
            pass
        return AnonymousUser()
