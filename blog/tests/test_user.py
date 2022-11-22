from typing import Callable, Dict
import pytest
from strawberry.test import Response


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_password_change(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()

    password_change_input = {
        "passwordChangeInput": {
            "oldPassword": "admin_password_155",
            "newPassword1": "admin+20",
            "newPassword2": "admin+20",
        }
    }

    query: str = import_query("passwordChange.graphql")
    response: Response = client_query(query, password_change_input)

    assert response is not None
    password_change: Dict = response.data.get("passwordChange", None)
    assert password_change is not None

    success: Dict = password_change.get("success", None)
    assert success is not None
    assert success is True

    errors: Dict = password_change.get("errors", None)
    assert errors is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_password_change_to_same_password(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()

    password_change_input = {
        "passwordChangeInput": {
            "oldPassword": "admin_password_155",
            "newPassword1": "admin_password_155",
            "newPassword2": "admin_password_155",
        }
    }

    query: str = import_query("passwordChange.graphql")
    response: Response = client_query(query, password_change_input)

    assert response is not None
    password_change: Dict = response.data.get("passwordChange", None)
    assert password_change is not None

    success: Dict = password_change.get("success", None)
    assert success is not None
    assert success is True

    errors: Dict = password_change.get("errors", None)
    assert errors is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_password_change_wrong_old_password(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()

    password_change_input = {
        "passwordChangeInput": {
            "oldPassword": "wrongPassword",
            "newPassword1": "admin+20",
            "newPassword2": "admin+20",
        }
    }

    query: str = import_query("passwordChange.graphql")
    response: Response = client_query(query, password_change_input)

    assert response is not None
    password_change: Dict = response.data.get("passwordChange", None)
    assert password_change is not None

    success: Dict = password_change.get("success", None)
    assert success is not None
    assert success is False

    errors: Dict = password_change.get("errors", None)
    assert errors is not None

    old_password: Dict = errors.get("old_password", None)
    assert old_password is not None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_password_change_new_password_mismatch(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()

    password_change_input = {
        "passwordChangeInput": {
            "oldPassword": "admin_password_155",
            "newPassword1": "admin+20",
            "newPassword2": "admin+40",
        }
    }

    query: str = import_query("passwordChange.graphql")
    response: Response = client_query(query, password_change_input)

    assert response is not None
    password_change: Dict = response.data.get("passwordChange", None)
    assert password_change is not None

    success: Dict = password_change.get("success", None)
    assert success is not None
    assert success is False

    errors: Dict = password_change.get("errors", None)
    assert errors is not None

    new_password2: Dict = errors.get("new_password2", None)
    assert new_password2 is not None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_password_change_password_too_common(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()

    password_change_input = {
        "passwordChangeInput": {
            "oldPassword": "admin_password_155",
            "newPassword1": "password123",
            "newPassword2": "password123",
        }
    }

    query: str = import_query("passwordChange.graphql")
    response: Response = client_query(query, password_change_input)

    assert response is not None
    password_change: Dict = response.data.get("passwordChange", None)
    assert password_change is not None

    success: Dict = password_change.get("success", None)
    assert success is not None
    assert success is False

    errors: Dict = password_change.get("errors", None)
    assert errors is not None

    new_password2: Dict = errors.get("new_password2", None)
    assert new_password2 is not None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_password_change_similar_to_username(
    auth: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    auth()

    password_change_input = {
        "passwordChangeInput": {
            "oldPassword": "admin_password_155",
            "newPassword1": "jane.doe-blogapp-lo",
            "newPassword2": "jane.doe-blogapp-lo",
        }
    }

    query: str = import_query("passwordChange.graphql")
    response: Response = client_query(query, password_change_input)

    assert response is not None
    password_change: Dict = response.data.get("passwordChange", None)
    assert password_change is not None

    success: Dict = password_change.get("success", None)
    assert success is not None
    assert success is False

    errors: Dict = password_change.get("errors", None)
    assert errors is not None

    new_password2: Dict = errors.get("new_password2", None)
    assert new_password2 is not None
