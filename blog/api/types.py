import typing

from strawberry import auto
import strawberry
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

    is_liked: bool
    like_count: int
    comment_count: int
    tags: typing.List['Tag']

    def resolve_tags(self, info):
        return self.tags.all()

    def resolve_is_liked(self, info):
        user = info.context.user
        if user.is_authenticated:
            return (
                len(
                    list(
                        filter(
                            lambda post_like: post_like.user == user,
                            self.post_likes.all(),
                        )
                    )
                )
                > 0
            )
        return False

    def resolve_like_count(self, info):
        return self.post_likes.count()

    def resolve_comment_count(self, info):
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
