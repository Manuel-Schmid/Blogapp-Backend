import strawberry
from blog.models import User, UserStatus


class AuthMutations:
    @strawberry.mutation
    def register(
        self, email: str, username: str, password1: str, password2: str
    ) -> bool:
        if password1 != password2:
            return False

        user = User.objects.create(email=email, username=username)
        user.set_password(password1)
        user.save()
        user_status = UserStatus.objects.create(
            user=user, verified=False, archived=False, secondary_email=None
        )
        user_status.send_activation_email()

        return True
