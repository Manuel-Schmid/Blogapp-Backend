import inspect
from functools import wraps
from typing import Any, Coroutine

import django
from django.contrib.auth import get_user_model
from django.core.handlers.asgi import ASGIRequest
from strawberry.types import Info
from strawberry_django.utils import is_async
from strawberry_django_jwt import exceptions, signals
from strawberry_django_jwt.auth import authenticate
from strawberry_django_jwt.decorators import (
    user_passes_test,
    on_token_auth_resolve_async,
    setup_jwt_cookie,
    csrf_rotation,
    refresh_expiration,
    on_token_auth_resolve,
)
from strawberry_django_jwt.utils import get_context, maybe_thenable
from blog.models import UserStatus

author_permission_required = user_passes_test(lambda u: UserStatus.objects.get(user=u).is_author)


def token_auth(f: Any) -> Coroutine:  # noqa: ANN401 todo
    async def wrapper_async(cls: Any, info: Info, password: str, **kwargs: Any) -> Coroutine:  # noqa: ANN401 todo
        context = get_context(info)
        context._jwt_token_auth = True
        username = kwargs.get(get_user_model().USERNAME_FIELD)
        user = await authenticate(
            request=context,
            username=username,
            password=password,
        )
        if user is None:
            raise exceptions.JSONWebTokenError(
                "Please enter valid credentials",
            )

        user_status = UserStatus.objects.get(user=user)

        if not user_status.verified:
            raise exceptions.JSONWebTokenError(
                "This user has not yet been verified",
            )

        context.user = user

        result = f(cls, info, **kwargs)
        signals.token_issued.send(sender=cls, request=context, user=user)
        return await maybe_thenable((info, user, result), on_token_auth_resolve_async)

    @wraps(f)
    @setup_jwt_cookie
    @csrf_rotation
    @refresh_expiration
    def wrapper(cls: Any, info: Info, password: str, **kwargs: Any) -> Coroutine:  # noqa: ANN401 todo
        context = get_context(info)
        if inspect.isawaitable(f) or (isinstance(context, ASGIRequest) and is_async()):
            return wrapper_async(cls, info, password, **kwargs)
        context._jwt_token_auth = True
        username = kwargs.get(get_user_model().USERNAME_FIELD)
        user = django.contrib.auth.authenticate(
            request=context,
            username=username,
            password=password,
        )
        if user is None:
            raise exceptions.JSONWebTokenError(
                "Please enter valid credentials",
            )

        user_status = UserStatus.objects.get(user=user)

        if not user_status.verified:
            raise exceptions.JSONWebTokenError(
                "This user has not yet been verified",
            )

        context.user = user

        result = f(cls, info, **kwargs)
        signals.token_issued.send(sender=cls, request=context, user=user)
        return maybe_thenable((info, user, result), on_token_auth_resolve)

    return wrapper
