from typing import Dict, Optional, Callable
import pytest
from strawberry.test import Response

from blog.models import User, UserStatus


@pytest.mark.django_db
def test_login(
    login: Callable,
    create_user: Callable,
    import_query: Callable,
    client_query: Callable,
    logout: Callable,
) -> None:
    username: str = 'jane.doe@blogapp.lo'
    password: str = 'password'

    # create a user
    user: User = create_user(username=username)
    user.set_password(password)
    user.save()

    UserStatus.objects.create(
        user=user,
        verified=True,
        archived=False,
        secondary_email=False,
        is_author=False,
    )

    # no access to profile before login
    query: str = import_query('me.graphql')
    response: Response = client_query(query, None)

    assert response is not None
    assert response.errors is not None

    extensions = response.errors[0].get('extensions', None)
    code = extensions.get('code', None)
    assert code is not None
    assert code == 'PERMISSION_DENIED'

    # login
    login(username, password)

    # access to profile with login
    query: str = import_query('me.graphql')
    response: Response = client_query(query)

    assert response is not None
    assert response.errors is None

    me: Optional[Dict] = response.data.get('me', None)
    assert me is not None
    assert me.get('username', None) == username

    # logout
    logout()

    # no access to profile after login
    query: str = import_query('me.graphql')
    response: Response = client_query(query, None)

    assert response is not None
    assert response.errors is not None
    extensions = response.errors[0].get('extensions', None)
    code = extensions.get('code', None)
    assert code is not None
    assert code == 'PERMISSION_DENIED'
