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
    id: auto
    slug: str
    name: auto


@gql.django.type(UserModel)
class User:
    id: auto
    posts: auto
    email: auto
    password: auto
    username: auto
    first_name: auto
    last_name: auto


@gql.django.type(TagModel)
class Tag:
    slug: auto
    name: auto


@gql.django.type(PostModel)
class Post:
    id: auto
    title: auto
    slug: str
    text: auto
    image: auto
    category: auto
    comments: auto
    post_likes: auto
    owner: auto
    date_created: auto

    is_liked: bool
    like_count: int
    comment_count: int
    tags: typing.List[Tag]

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


@gql.django.type(PostModel)
class PaginationPosts:
    posts: typing.List[Post]
    num_post_pages: int


@gql.django.type(CommentModel)
class Comment:
    id: auto
    title: auto
    text: auto
    post: auto
    owner: auto


@gql.django.type(PostLikeModel)
class PostLike:
    id: auto
    post: auto
    user: auto


@gql.django.type(CommentLikeModel)
class CommentLike:
    id: auto
    comment: auto
    user: auto
