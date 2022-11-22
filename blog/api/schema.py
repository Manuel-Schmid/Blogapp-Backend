import strawberry
from strawberry_django_plus.directives import SchemaDirectiveExtension
from strawberry_django_plus.optimizer import DjangoOptimizerExtension
from strawberry_django_jwt.middleware import JSONWebTokenMiddleware

from .mutations import (
    AuthMutation,
    CategoryMutations,
    PostMutations,
    CommentMutations,
    PostLikeMutations,
    AuthorRequestMutations,
)
from .queries import UserQueries, PostQueries, CategoryQueries, TagQueries, AuthorRequestQueries


@strawberry.type
class RootQuery(UserQueries, PostQueries, CategoryQueries, TagQueries, AuthorRequestQueries):
    pass


@strawberry.type
class RootMutation(
    AuthMutation,
    CategoryMutations,
    PostMutations,
    CommentMutations,
    PostLikeMutations,
    AuthorRequestMutations,
):
    pass


schema = strawberry.Schema(
    query=RootQuery,
    mutation=RootMutation,
    extensions=[
        JSONWebTokenMiddleware,
        SchemaDirectiveExtension,
        DjangoOptimizerExtension,
    ],
)
