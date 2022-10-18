import strawberry
from strawberry_django_plus.directives import SchemaDirectiveExtension
from strawberry_django_plus.optimizer import DjangoOptimizerExtension
from strawberry_django_jwt.middleware import JSONWebTokenMiddleware

from .mutations import AuthMutation
from .queries import UserQuery


@strawberry.type
class RootQuery(UserQuery):
    pass


@strawberry.type
class RootMutation(AuthMutation):
    pass


schema = strawberry.Schema(
    query=RootQuery,
    mutation=RootMutation,
    extensions=[
        JSONWebTokenMiddleware,
        SchemaDirectiveExtension,
        DjangoOptimizerExtension,
    ]
)
