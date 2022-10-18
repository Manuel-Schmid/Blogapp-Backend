from typing import Optional

import strawberry
from strawberry.types import Info
from strawberry_django_jwt.decorators import login_required

from blog.api.types import User
from blog import models


@strawberry.type
class UserQuery:
    @strawberry.field
    @login_required
    def me(self, info: Info) -> Optional[User]:
        try:
            return models.User.objects.get(pk=info.context.request.user.id)
        except models.User.DoesNotExist:
            return None
