import strawberry
from blog.forms import UserForm
from blog.models import UserStatus
from blog.api.inputs import UserRegistrationInput
from blog.api.types import RegisterType


class AuthMutations:
    @strawberry.mutation
    def register(
        self, user_registration_input: UserRegistrationInput
    ) -> RegisterType:
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

        return RegisterType(success=not has_errors, errors=errors if errors else None)
