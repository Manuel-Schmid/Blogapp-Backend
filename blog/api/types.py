import typing
from datetime import datetime

from strawberry import auto
import strawberry
from strawberry.scalars import JSON
from strawberry.types import Info
from strawberry_django_plus import gql
from taggit.models import Tag as TagModel

from blog.api.inputs import PostStatus
from blog.models import (
    Category as CategoryModel,
    User as UserModel,
    UserStatus as UserStatusModel,
    Post as PostModel,
    Comment as CommentModel,
    PostLike as PostLikeModel,
    CommentLike as CommentLikeModel,
    AuthorRequest as AuthorRequestModel,
    PostRelation as PostRelationModel,
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
class ResendActivationEmailType(BaseGraphQLType):
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
class UpdateAccountType(BaseGraphQLType):
    success: bool


@strawberry.type
class EmailChangeType(BaseGraphQLType):
    success: bool
    user: typing.Optional['User']


@strawberry.type
class AuthorRequestWrapperType(BaseGraphQLType):
    success: bool
    author_request: typing.Optional['AuthorRequest']


@gql.django.type(PostModel)
class PostTitleTuple:
    id: strawberry.ID
    title: str


@gql.django.type(AuthorRequestModel)
class AuthorRequest:
    id: strawberry.ID
    date_opened: datetime
    date_closed: typing.Optional[datetime]
    status: str
    user: 'User'


@gql.django.type(AuthorRequestModel)
class PaginationAuthorRequests:
    author_requests: typing.List[AuthorRequest]
    num_pages: int


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
    category: Category
    comments: typing.List['Comment']
    owner: 'User'
    date_created: auto
    status: PostStatus

    @strawberry.field
    def related_sub_posts(self) -> typing.List['Post']:
        return PostModel.objects.filter(related_sub_posts__main_post_id__exact=self.id)

    @strawberry.field
    def related_main_posts(self) -> typing.List['Post']:
        return PostModel.objects.filter(related_main_posts__sub_post_id__exact=self.id)

    @strawberry.field
    def tags(self) -> typing.List[Tag]:
        return TagModel.objects.filter(taggit_taggeditem_items__object_id__exact=self.id)

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


@strawberry.type
class CreatePostType(BaseGraphQLType):
    post: typing.Optional[Post]
    success: bool


@strawberry.type
class UpdatePostType(BaseGraphQLType):
    post: typing.Optional[Post]
    success: bool


@strawberry.type
class UpdatePostStatusType(BaseGraphQLType):
    success: bool
    post: typing.Optional[Post]


@gql.django.type(UserStatusModel)
class UserStatus:
    id: strawberry.ID
    user: 'User'
    verified: bool
    archived: bool
    secondary_email: typing.Optional[str]
    is_author: bool


@gql.django.type(UserModel)
class User:
    id: strawberry.ID
    posts: typing.List[Post]
    email: str
    password: str
    username: str
    first_name: str
    last_name: str
    is_superuser: bool
    is_staff: bool
    is_active: bool
    user_status: UserStatus


@gql.django.type(PostModel)
class PaginationPosts:
    posts: typing.List[Post]
    num_post_pages: int


@gql.django.type(CommentModel)
class Comment:
    id: strawberry.ID
    title: str
    text: str
    post: Post
    owner: User


@gql.django.type(PostLikeModel)
class PostLike:
    id: strawberry.ID
    post: Post
    user: User


@gql.django.type(PostRelationModel)
class PostRelationType:
    main_post: strawberry.ID
    sub_post: strawberry.ID


@gql.django.type(CommentLikeModel)
class CommentLike:
    id: strawberry.ID
    comment: Comment
    user: User
