import strawberry
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from strawberry.types import Info

from blog.forms import UserForm, EmailChangeForm
from blog.models import UserStatus, User
from blog.api.inputs import (
    UserRegistrationInput,
    PasswordChangeInput,
    PasswordResetInput,
    EmailChangeInput,
)
from blog.api.types import (
    RegisterAccountType,
    VerifyAccountType,
    PasswordChangeType,
    PasswordResetType,
    SendPasswordResetEmailType,
    SendEmailChangeEmailType,
    EmailChangeType,
)
from blog.utils import TokenAction, get_token_payload


class AuthMutations:
    @strawberry.mutation
    def register(
        self, user_registration_input: UserRegistrationInput
    ) -> RegisterAccountType:
        errors = {}
        has_errors = False

        form = UserForm(data=vars(user_registration_input))
        if not form.is_valid():
            has_errors = True
            errors.update(form.errors.get_json_data())

        if not has_errors:
            user = form.save()
            user_status = UserStatus.objects.create(
                user=user, verified=False, archived=False, secondary_email=None
            )
            user_status.send_activation_email()

        return RegisterAccountType(
            success=not has_errors, errors=errors if errors else None
        )

    @strawberry.mutation
    def verify_account(self, token: str) -> VerifyAccountType:
        return VerifyAccountType(success=UserStatus.verify(token))

    @strawberry.mutation
    def password_change(
        self, info: Info, password_change_input: PasswordChangeInput
    ) -> PasswordChangeType:
        errors = {}
        has_errors = False

        user = info.context.request.user
        if user.is_authenticated:
            form = PasswordChangeForm(user=user, data=vars(password_change_input))

            if not form.is_valid():
                has_errors = True
                errors.update(form.errors.get_json_data())

            if not has_errors:
                form.save()

            return PasswordChangeType(
                success=not has_errors, errors=errors if errors else None
            )

    @strawberry.mutation
    def send_password_reset_email(self, email: str) -> SendPasswordResetEmailType:
        user = User.objects.get(email=email)
        UserStatus.objects.get(user=user).send_password_reset_email()
        return SendPasswordResetEmailType(success=True)

    @strawberry.mutation
    def password_reset(
        self, password_reset_input: PasswordResetInput
    ) -> PasswordResetType:
        errors = {}
        has_errors = False

        payload = get_token_payload(
            password_reset_input.token, TokenAction.PASSWORD_RESET
        )
        if payload:
            user = User.objects.get(**payload)
            form = SetPasswordForm(user=user, data=vars(password_reset_input))

            if not form.is_valid():
                has_errors = True
                errors.update(form.errors.get_json_data())

            if not has_errors:
                form.save()

        else:
            has_errors = True
            errors.update({'token': 'Invalid Token'})

        return PasswordResetType(
            success=not has_errors, errors=errors if errors else None
        )

    @strawberry.mutation
    def send_email_change_email(self, email: str) -> SendEmailChangeEmailType:
        user = User.objects.get(email=email)
        UserStatus.objects.get(user=user).send_email_change_email()
        return SendEmailChangeEmailType(success=True)

    @strawberry.mutation
    def email_change(self, email_change_input: EmailChangeInput) -> EmailChangeType:
        errors = {}
        has_errors = False

        payload = get_token_payload(email_change_input.token, TokenAction.EMAIL_CHANGE)
        if payload:
            user = User.objects.get(**payload)
            form = EmailChangeForm(user=user, data=vars(email_change_input))

            if not form.is_valid():
                has_errors = True
                errors.update(form.errors.get_json_data())

            if not has_errors:
                form.save()
        else:
            has_errors = True
            errors.update({'token': 'Invalid Token'})

        return EmailChangeType(
            success=not has_errors, errors=errors if errors else None
        )
