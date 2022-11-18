from strawberry_django_jwt.decorators import user_passes_test
from blog.models import UserStatus

author_permission_required = user_passes_test(
    lambda u: UserStatus.objects.get(user=u).is_author
)
