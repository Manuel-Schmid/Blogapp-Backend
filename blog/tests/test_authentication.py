from typing import Callable, Dict
import pytest
from django.core import mail
from strawberry.test import Response
from django.conf import settings

from blog.models import User, UserStatus


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_register_and_verify(
    get_token_from_mail: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    user_registration_input = {
        'userRegistrationInput': {
            'email': 'admin@admin.com',
            'username': 'abc',
            'password1': 'helloWorld++x',
            'password2': 'helloWorld++x',
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
    token = get_token_from_mail(mail.outbox[0].body, settings.ACTIVATION_PATH_ON_EMAIL)
    assert token is not None

    user = User.objects.get(username='abc')
    user_status = UserStatus.objects.get(user=user)
    assert user_status.verified is False

    activation_token = {
        'token': token,
    }

    query: str = import_query('verifyAccount.graphql')
    response: Response = client_query(query, activation_token)

    assert response is not None
    verify_account: Dict = response.data.get('verifyAccount', None)
    assert verify_account is not None

    success: Dict = verify_account.get('success', None)
    assert success is not None
    assert success is True
    user_status = UserStatus.objects.get(user=user)
    assert user_status.verified is True


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
            'password2': 'helloWorld++x',
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
        'token': 'invalid_test_token',
    }

    query: str = import_query('verifyAccount.graphql')
    response: Response = client_query(query, token)

    assert response is not None
    verify_account: Dict = response.data.get('verifyAccount', None)
    assert verify_account is not None

    success: Dict = verify_account.get('success', None)
    assert success is not None
    assert success is False


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_password_reset(
    get_token_from_mail: Callable,
    create_users: Callable,
    login: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_users()

    email = {
        'email': 'user1@example.com',
    }

    query: str = import_query('sendPasswordResetEmail.graphql')
    response: Response = client_query(query, email)

    assert response is not None
    send_password_reset_email: Dict = response.data.get('sendPasswordResetEmail', None)
    assert send_password_reset_email is not None

    success: Dict = send_password_reset_email.get('success', None)
    assert success is not None
    assert success is True

    errors: Dict = send_password_reset_email.get('errors', None)
    assert errors is None

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['user1@example.com']
    token = get_token_from_mail(mail.outbox[0].body, settings.PASSWORD_RESET_PATH_ON_EMAIL)
    assert token is not None

    password_reset_input = {
        'passwordResetInput': {
            'newPassword1': 'admin_password_201',
            'newPassword2': 'admin_password_201',
            'token': token,
        }
    }

    query: str = import_query('passwordReset.graphql')
    response: Response = client_query(query, password_reset_input)

    assert response is not None
    password_reset: Dict = response.data.get('passwordReset', None)
    assert password_reset is not None

    success: Dict = password_reset.get('success', None)
    assert success is not None
    assert success is True

    errors: Dict = password_reset.get('errors', None)
    assert errors is None

    login_response: Response = login('test_user1', 'admin_password_201')
    assert login_response is not None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_password_reset_invalid_token(
    import_query: Callable,
    client_query: Callable,
) -> None:
    password_reset_input = {
        'passwordResetInput': {
            'newPassword1': 'admin_password_201',
            'newPassword2': 'admin_password_201',
            'token': 'invalid_test_token',
        }
    }

    query: str = import_query('passwordReset.graphql')
    response: Response = client_query(query, password_reset_input)

    assert response is not None
    password_reset: Dict = response.data.get('passwordReset', None)
    assert password_reset is not None

    success: Dict = password_reset.get('success', None)
    assert success is not None
    assert success is False

    errors: Dict = password_reset.get('errors', None)
    assert errors is not None
    assert errors.get('token', None) is not None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_email_change(
    get_token_from_mail: Callable,
    create_users: Callable,
    import_query: Callable,
    client_query: Callable,
) -> None:
    create_users()

    email = {
        'email': 'user1@example.com',
    }

    query: str = import_query('sendEmailChangeEmail.graphql')
    response: Response = client_query(query, email)

    assert response is not None
    send_password_reset_email: Dict = response.data.get('sendEmailChangeEmail', None)
    assert send_password_reset_email is not None

    success: Dict = send_password_reset_email.get('success', None)
    assert success is not None
    assert success is True

    errors: Dict = send_password_reset_email.get('errors', None)
    assert errors is None

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['user1@example.com']
    token = get_token_from_mail(mail.outbox[0].body, settings.EMAIL_CHANGE_PATH_ON_EMAIL)
    assert token is not None

    email_change_input = {
        'emailChangeInput': {
            'newEmail1': 'new_email@example.com',
            'newEmail2': 'new_email@example.com',
            'token': token,
        }
    }

    query: str = import_query('emailChange.graphql')
    response: Response = client_query(query, email_change_input)

    assert response is not None
    email_change: Dict = response.data.get('emailChange', None)
    assert email_change is not None

    success: Dict = email_change.get('success', None)
    assert success is not None
    assert success is True

    errors: Dict = email_change.get('errors', None)
    assert errors is None

    assert User.objects.get(username='test_user1').email == 'new_email@example.com'
