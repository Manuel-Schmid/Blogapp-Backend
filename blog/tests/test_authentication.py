from typing import Callable, Dict
import pytest
from django.core import mail
from strawberry.test import Response


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_register(
        import_query: Callable,
        client_query: Callable,
) -> None:
    user_registration_input = {
        'userRegistrationInput': {
            'email': 'admin@admin.com',
            'username': 'abc',
            'password1': 'helloWorld++x',
            'password2': 'helloWorld++x'
        }
    }

    query: str = import_query('register.graphql')
    response: Response = client_query(query, user_registration_input)

    assert response is not None
    register: Dict = response.data.get('register', None)
    assert register is not None

    success: Dict = register.get('success', None)
    assert success is not None
    assert success is True

    errors: Dict = register.get('errors', None)
    assert errors is None

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['admin@admin.com']


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_register_duplicate_email(
        import_query: Callable,
        client_query: Callable,
) -> None:
    user_registration_input = {
        'userRegistrationInput': {
            'email': 'admin@admin.com',
            'username': 'abc',
            'password1': 'helloWorld++x',
            'password2': 'helloWorld++x'
        }
    }

    query: str = import_query('register.graphql')
    client_query(query, user_registration_input)
    response: Response = client_query(query, user_registration_input)

    assert response is not None
    register: Dict = response.data.get('register', None)
    assert register is not None

    success: Dict = register.get('success', None)
    assert success is not None
    assert success is False

    errors: Dict = register.get('errors', None)
    assert errors is not None
    assert 'username' in errors

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['admin@admin.com']


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_verify_invalid_token(
        import_query: Callable,
        client_query: Callable,
) -> None:
    token = {
        'token': 'test_token',
    }

    query: str = import_query('verifyAccount.graphql')
    response: Response = client_query(query, token)

    assert response is not None
    verify_account: Dict = response.data.get('verifyAccount', None)
    assert verify_account is not None

    success: Dict = verify_account.get('success', None)
    assert success is not None
    assert success is False
