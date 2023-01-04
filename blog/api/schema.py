import strawberry
from graphql import GraphQLError
from strawberry.types import ExecutionContext
from strawberry_django_jwt.exceptions import PermissionDenied, JSONWebTokenExpired, JSONWebTokenError
from strawberry_django_plus.directives import SchemaDirectiveExtension
from strawberry_django_plus.optimizer import DjangoOptimizerExtension
from strawberry_django_jwt.middleware import JSONWebTokenMiddleware
from typing import List, Optional
from .mutations import (
    AuthMutation,
    CategoryMutations,
    PostMutations,
    CommentMutations,
    PostLikeMutations,
    AuthorRequestMutations,
    ObtainJSONWebToken,
)
from .queries import UserQueries, PostQueries, CategoryQueries, TagQueries, AuthorRequestQueries


@strawberry.type
class RootQuery(UserQueries, PostQueries, CategoryQueries, TagQueries, AuthorRequestQueries):
    pass


@strawberry.type
class RootMutation(
    ObtainJSONWebToken,
    AuthMutation,
    CategoryMutations,
    PostMutations,
    CommentMutations,
    PostLikeMutations,
    AuthorRequestMutations,
):
    pass


class Schema(strawberry.Schema):
    def process_errors(
        self,
        errors: List[GraphQLError],
        execution_context: Optional[ExecutionContext] = None,
    ) -> None:
        for error in errors:
            actual_error = error.original_error or error
            error_code = getattr(actual_error, 'error_code', 'GENERIC_ERROR')
            if isinstance(actual_error, PermissionDenied):
                error_code = 'PERMISSION_DENIED'
            elif isinstance(actual_error, JSONWebTokenExpired):
                error_code = 'TOKEN_EXPIRED'
            elif isinstance(actual_error, JSONWebTokenError):
                error_code = 'TOKEN_INVALID'

            error.extensions['code'] = error_code


schema = Schema(
    query=RootQuery,
    mutation=RootMutation,
    extensions=[
        JSONWebTokenMiddleware,
        SchemaDirectiveExtension,
        DjangoOptimizerExtension,
    ],
)
