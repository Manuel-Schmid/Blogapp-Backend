import strawberry
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from strawberry.types import Info
from strawberry_django_jwt.decorators import login_required

from blog.forms import UserForm, UpdateAccountForm, EmailChangeForm
from blog.api.inputs import (
    UserRegistrationInput,
    PasswordChangeInput,
    PasswordResetInput,
    EmailChangeInput,
    UpdateAccountInput,
)
from blog.api.types import (
    RegisterAccountType,
    VerifyAccountType,
    PasswordChangeType,
    PasswordResetType,
    SendPasswordResetEmailType,
    SendEmailChangeEmailType,
    EmailChangeType,
    ResendActivationEmailType,
    UpdateAccountType,
)
from blog.models import User, UserStatus, UserProfile
from blog.utils import TokenAction, get_token_payload


class AuthMutations:
    @strawberry.mutation
    def register(self, info: Info, user_registration_input: UserRegistrationInput) -> RegisterAccountType:
        errors = {}
        has_errors = False
        files = info.context.request.FILES

        if len(files) != 1:
            has_errors = True
            errors.update({'file': 'You must upload exactly one image file as avatar'})

        if not has_errors:
            form = UserForm(data=vars(user_registration_input), files={'avatar': files['1']})
            if not form.is_valid():
                has_errors = True
                errors.update(form.errors.get_json_data())

            if not has_errors:
                user = form.save()
                user_status = UserStatus.objects.create(user=user, verified=False, archived=False, secondary_email=None)
                UserProfile.objects.create(user=user)
                user_status.send_activation_email()

        return RegisterAccountType(success=not has_errors, errors=errors if errors else None)

    @strawberry.mutation
    def resend_activation_email(self, email: str) -> ResendActivationEmailType:
        errors = {}
        has_errors = False

        user = User.objects.get(email=email)
        user_status = UserStatus.objects.get(user=user)

        if user_status.verified:
            has_errors = True
            errors.update({'userStatus': 'User already verified'})
        else:
            user_status.send_activation_email()

        return ResendActivationEmailType(success=not has_errors, errors=errors if errors else None)

    @strawberry.mutation
    def verify_account(self, token: str) -> VerifyAccountType:
        return VerifyAccountType(success=UserStatus.verify(token))

    @login_required
    @strawberry.mutation
    def password_change(self, info: Info, password_change_input: PasswordChangeInput) -> PasswordChangeType:
        errors = {}
        has_errors = False

        user = info.context.request.user
        form = PasswordChangeForm(user=user, data=vars(password_change_input))

        if not form.is_valid():
            has_errors = True
            errors.update(form.errors.get_json_data())

        if not has_errors:
            form.save()

        return PasswordChangeType(success=not has_errors, errors=errors if errors else None)

    @strawberry.mutation
    def send_password_reset_email(self, email: str) -> SendPasswordResetEmailType:
        user = User.objects.get(email=email)
        UserStatus.objects.get(user=user).send_password_reset_email()
        return SendPasswordResetEmailType(success=True)

    @strawberry.mutation
    def password_reset(self, password_reset_input: PasswordResetInput) -> PasswordResetType:
        errors = {}
        has_errors = False

        payload = get_token_payload(password_reset_input.token, TokenAction.PASSWORD_RESET)
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

        return PasswordResetType(success=not has_errors, errors=errors if errors else None)

    @login_required
    @strawberry.mutation
    def update_account(self, info: Info, update_account_input: UpdateAccountInput) -> UpdateAccountType:
        errors = {}
        has_errors = False

        user = info.context.request.user
        if not UserStatus.objects.get(user=user).verified:
            has_errors = True
            errors.update({'user': 'User not verified'})

        form = UpdateAccountForm(instance=user, data=vars(update_account_input))

        if not form.is_valid():
            has_errors = True
            errors.update(form.errors.get_json_data())

        if not has_errors:
            form.save()

        return UpdateAccountType(success=not has_errors, errors=errors if errors else None)

    @strawberry.mutation
    def send_email_change_email(self, email: str) -> SendEmailChangeEmailType:
        user = User.objects.get(email=email)
        UserStatus.objects.get(user=user).send_email_change_email()
        return SendEmailChangeEmailType(success=True)

    @strawberry.mutation
    def email_change(self, email_change_input: EmailChangeInput) -> EmailChangeType:
        errors = {}
        has_errors = False
        user = None

        if email_change_input.new_email1 != email_change_input.new_email2:
            has_errors = True
            errors.update({'email_mismatch': 'The two email address fields did not match'})

        else:
            payload = get_token_payload(email_change_input.token, TokenAction.EMAIL_CHANGE)
            if payload:
                user = User.objects.get(**payload)
                form = EmailChangeForm(instance=user, data={'email': email_change_input.new_email1})

                if not form.is_valid():
                    has_errors = True
                    errors.update(form.errors.get_json_data())

                if not has_errors:
                    form.save()
            else:
                has_errors = True
                errors.update({'token': 'Invalid Token'})

        return EmailChangeType(
            success=not has_errors,
            errors=errors if errors else None,
            user=user if not has_errors else None,
        )
