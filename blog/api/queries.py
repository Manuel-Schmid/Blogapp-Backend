import typing
from typing import Optional

import strawberry
from django.core.paginator import Paginator
from django.db.models import Q
from strawberry.types import Info
from strawberry_django_jwt.decorators import login_required, superuser_required

from blog.api.types import (
    Category as CategoryType,
    User as UserType,
    Tag as TagType,
    Post as PostType,
    PaginationPosts as PaginationPostsType,
    AuthorRequest as AuthorRequestType,
    PaginationAuthorRequests as PaginationAuthorRequestsType,
)

from taggit.models import Tag, TaggedItem
from ..models import Category, Post, User, AuthorRequest


@strawberry.type
class UserQueries:
    @strawberry.field
    @login_required
    def me(self, info: Info) -> Optional[UserType]:
        try:
            return User.objects.get(pk=info.context.request.user.id)
        except User.DoesNotExist:
            return None

    @strawberry.field
    def users(self) -> typing.List[UserType]:
        return User.objects.select_related('user_status').all()

    @strawberry.field
    def user(self, info: Info) -> Optional[UserType]:
        user = info.context.request.user
        if user.is_authenticated:
            return User.objects.select_related('user_status').get(pk=user.id)
        return None


@strawberry.type
class CategoryQueries:
    @strawberry.field
    def categories(self) -> typing.List[CategoryType]:
        return Category.objects.all()

    @strawberry.field
    def category_by_id(self, id: strawberry.ID) -> CategoryType:
        return Category.objects.get(pk=id)


@strawberry.type
class TagQueries:
    @strawberry.field
    def tags(self) -> typing.List[TagType]:
        return Tag.objects.all()

    @strawberry.field
    def used_tags(
        self,
        category_slug: Optional[str] = None,
    ) -> typing.List[TagType]:
        tag_filter = Q()
        if category_slug is not None:
            category_posts = list(
                Post.objects.select_related('category')
                .prefetch_related('tags')
                .filter(category__slug=category_slug)
                .values_list('id', flat=True)
            )
            tag_filter &= Q(object_id__in=category_posts)

        tags = [obj.tag for obj in TaggedItem.objects.select_related('tag').filter(tag_filter)]
        return list(set(tags))


@strawberry.type
class AuthorRequestQueries:
    @superuser_required
    @strawberry.field
    def paginated_author_requests(
        self, status: Optional[str] = None, sort: Optional[str] = None, active_page: Optional[int] = 1
    ) -> PaginationAuthorRequestsType:
        request_filter = Q()
        if status:
            request_filter &= Q(status=status)

        author_requests = AuthorRequest.objects.filter(request_filter)
        if sort:
            author_requests = author_requests.order_by(sort)
        author_requests = list([obj for obj in author_requests])

        paginator = Paginator(author_requests, 8)
        return PaginationAuthorRequestsType(author_requests=paginator.page(active_page), num_pages=paginator.num_pages)

    @login_required
    @strawberry.field
    def author_request_by_user(self, info: Info) -> Optional[AuthorRequestType]:
        user = info.context.request.user
        return AuthorRequest.objects.get(user=user)


@strawberry.type
class PostQueries:
    @staticmethod
    def posts() -> typing.List[PostType]:
        return Post.objects.select_related('category', 'owner').prefetch_related(
            'tags',
            'comments',
            'comments__owner',
            'post_likes',
            'post_likes__user',
            'owner__posts',
            'owner__posts__tags',
            'owner__posts__category',
        )

    @strawberry.field
    def paginated_posts(
        self,
        category_slug: Optional[str] = None,
        tag_slugs: Optional[str] = None,
        active_page: Optional[int] = 1,
    ) -> PaginationPostsType:

        post_filter = Q()
        if tag_slugs is not None:
            tag_slugs_list = tag_slugs.split(',')

            # or
            for tag in tag_slugs_list:
                post_filter |= Q(tagged_items__tag__slug__contains=tag)

            # and
            # tag_filter = Q()
            # for tag in tag_slugs_list:
            #     tag_filter |= Q(tag__slug=tag)
            # tagged_posts = list(
            #     TaggedItem.objects.select_related('tag')
            #     .values('object_id')
            #     .annotate(Count('object_id'))
            #     .filter(tag_filter)
            #     .filter(object_id__count=len(tag_slugs_list))
            #     .values_list('object_id', flat=True)
            # )
            # post_filter &= Q(id__in=tagged_posts)

        if category_slug is not None:
            post_filter &= Q(category__slug=category_slug)

        post_filter &= Q(status=Post.PostStatus.PUBLISHED)

        posts = PostQueries.posts().filter(post_filter)
        posts = list(set([obj for obj in posts]))

        paginator = Paginator(posts, 4)
        pagination_posts = PaginationPostsType()
        pagination_posts.posts = paginator.page(active_page)
        pagination_posts.num_post_pages = paginator.num_pages
        return pagination_posts

    @login_required
    @strawberry.field
    def paginated_user_posts(
        self,
        info: Info,
        active_page: Optional[int] = 1,
    ) -> PaginationPostsType:
        user = info.context.request.user

        posts = PostQueries.posts().filter(owner_id=user).order_by('-id')
        posts = list([obj for obj in posts])

        paginator = Paginator(posts, 6)
        pagination_posts = PaginationPostsType()
        pagination_posts.posts = paginator.page(active_page)
        pagination_posts.num_post_pages = paginator.num_pages
        return pagination_posts

    @strawberry.field
    def post_by_slug(self, info: Info, slug: str) -> Optional[PostType]:
        post = Post.objects.get(slug=slug)
        user = info.context.request.user
        if post.status == Post.PostStatus.PUBLISHED or user.is_authenticated and post.owner == user:
            return post
        return None
