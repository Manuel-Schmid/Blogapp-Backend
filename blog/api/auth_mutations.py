import strawberry
from django.contrib.auth.forms import PasswordChangeForm
from strawberry.types import Info

from blog.forms import UserForm
from blog.models import UserStatus
from blog.api.inputs import UserRegistrationInput, PasswordChangeInput
from blog.api.types import RegisterAccountType, VerifyAccountType, PasswordChangeType


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

        return RegisterAccountType(success=not has_errors, errors=errors if errors else None)

    @strawberry.mutation
    def verify_account(
            self, token: str
    ) -> VerifyAccountType:
        return VerifyAccountType(success=UserStatus.verify(token))

    @strawberry.mutation
    def password_change(self, info: Info, password_change_input: PasswordChangeInput) -> PasswordChangeType:
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

            return PasswordChangeType(success=not has_errors, errors=errors if errors else None)
