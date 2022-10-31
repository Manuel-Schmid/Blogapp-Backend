import typing

from strawberry import auto
import strawberry
from strawberry.scalars import JSON
from strawberry.types import Info
from strawberry_django_plus import gql
from taggit.models import Tag as TagModel
from blog.models import (
    Category as CategoryModel,
    User as UserModel,
    Post as PostModel,
    Comment as CommentModel,
    PostLike as PostLikeModel,
    CommentLike as CommentLikeModel,
)


@strawberry.type
class BaseGraphQLType:
    errors: typing.Optional[JSON]


@strawberry.type
class RegisterAccountType(BaseGraphQLType):
    success: bool


@strawberry.type
class VerifyAccountType:
    success: bool


@strawberry.type
class SendPasswordResetEmailType:
    success: bool


@strawberry.type
class SendEmailChangeEmailType:
    success: bool


@strawberry.type
class PasswordResetType(BaseGraphQLType):
    success: bool


@strawberry.type
class PasswordChangeType(BaseGraphQLType):
    success: bool


@strawberry.type
class EmailChangeType(BaseGraphQLType):
    success: bool
    user: typing.Optional['User']


@gql.django.type(CategoryModel)
class Category:
    id: strawberry.ID
    slug: str
    name: str


@gql.django.type(TagModel)
class Tag:
    slug: str
    name: str


@gql.django.type(PostModel)
class Post:
    id: strawberry.ID
    title: str
    slug: str
    text: str
    image: auto
    category: 'Category'
    comments: typing.List['Comment']
    owner: 'User'
    date_created: auto

    @strawberry.field
    def tags(self) -> typing.List['Tag']:
        return TagModel.objects.filter(
            taggit_taggeditem_items__object_id__exact=self.id
        )

    @strawberry.field
    def is_liked(self, info: Info) -> bool:
        user = info.context.request.user
        if user.is_authenticated:
            user_like_count = len(
                list(
                    filter(
                        lambda post_like: post_like.user == user,
                        self.post_likes.all(),
                    )
                )
            )
            return user_like_count > 0
        return False

    @strawberry.field
    def like_count(self) -> int:
        return self.post_likes.count()

    @strawberry.field
    def comment_count(self) -> int:
        return self.comments.count()


@gql.django.type(UserModel)
class User:
    id: strawberry.ID
    posts: typing.List['Post']
    email: str
    password: str
    username: str
    first_name: str
    last_name: str


@gql.django.type(PostModel)
class PaginationPosts:
    posts: typing.List['Post']
    num_post_pages: int


@gql.django.type(CommentModel)
class Comment:
    id: strawberry.ID
    title: str
    text: str
    post: 'Post'
    owner: 'User'


@gql.django.type(PostLikeModel)
class PostLike:
    id: strawberry.ID
    post: 'Post'
    user: 'User'


@gql.django.type(CommentLikeModel)
class CommentLike:
    id: strawberry.ID
    comment: 'Comment'
    user: 'User'
