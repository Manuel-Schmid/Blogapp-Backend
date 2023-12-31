import typing
from typing import Optional

import strawberry
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from strawberry.types import Info
from strawberry_django_jwt.decorators import login_required, superuser_required

from blog.api.types import (
    Category as CategoryType,
    User as UserType,
    Tag as TagType,
    PaginationPosts as PaginationPostsType,
    AuthorRequest as AuthorRequestType,
    PaginationAuthorRequests as PaginationAuthorRequestsType,
    PostTitleType,
    Subscription as SubscriptionType,
    DetailPost as DetailPostType,
)

from taggit.models import Tag, TaggedItem
from ..models import Category, Post, User, AuthorRequest, Subscription, Notification


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
            return User.objects.select_related('user_status', 'profile').get(pk=user.id)
        return None

    @strawberry.field
    def user_by_username(self, username: str) -> Optional[UserType]:
        return User.objects.get(username=username)


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
        if AuthorRequest.objects.filter(user=user).exists():
            return AuthorRequest.objects.get(user=user)
        else:
            return None


@strawberry.type
class SubscriptionQueries:
    @login_required
    @strawberry.field
    def user_subscriptions(self, info: Info, sort: Optional[str] = None) -> typing.List[SubscriptionType]:
        user = info.context.request.user
        subscriptions = Subscription.objects.filter(subscriber=user)
        if sort:
            subscriptions = subscriptions.order_by(sort)
        return subscriptions


@strawberry.type
class PostQueries:
    @staticmethod
    def posts() -> QuerySet:
        return Post.objects.select_related('category', 'owner').prefetch_related(
            'tags',
            'comments',
            'related_main_posts',
            'related_sub_posts',
            'comments__owner',
            'post_likes',
            'post_likes__user',
            'owner__posts',
            'owner__posts__tags',
            'owner__posts__category',
        )

    @staticmethod
    def paginate_posts(posts: QuerySet, per_page: int, active_page: int) -> PaginationPostsType:
        paginator = Paginator(posts, per_page)
        return PaginationPostsType(posts=paginator.page(active_page), num_post_pages=paginator.num_pages)

    @strawberry.field
    def post_titles(self, info: Info) -> typing.List[PostTitleType]:
        user = info.context.request.user
        post_filter = Q(status=Post.PostStatus.PUBLISHED)
        if user.is_authenticated:
            post_filter |= Q(owner=user)
        return Post.objects.filter(post_filter).only('title')

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

        return PostQueries.paginate_posts(posts, 4, active_page)

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

        return PostQueries.paginate_posts(posts, 6, active_page)

    @login_required
    @strawberry.field
    def paginated_notification_posts(
        self,
        info: Info,
        active_page: Optional[int] = 1,
    ) -> PaginationPostsType:
        user = info.context.request.user

        notification_post_ids = Notification.objects.filter(user=user).values_list('post_id', flat=True)
        post_filter = Q(id__in=notification_post_ids)
        post_filter &= Q(status=Post.PostStatus.PUBLISHED)
        posts = PostQueries.posts().filter(post_filter).order_by('-date_created')

        return PostQueries.paginate_posts(posts, 4, active_page)

    @strawberry.field
    def post_by_slug(self, info: Info, slug: str) -> Optional[DetailPostType]:
        errors = {}
        has_errors = False
        notification_removed = False
        user = info.context.request.user
        post = Post.objects.get(slug=slug)

        if not (post.status == Post.PostStatus.PUBLISHED or user.is_authenticated and post.owner == user):
            has_errors = True
            errors.update({'post': 'This post is not publicly available'})

        if not has_errors and user.is_authenticated:
            deleted_notifications = Notification.objects.filter(post=post, user=user).delete()[0]
            if deleted_notifications > 0:
                notification_removed = True

        return DetailPostType(
            post=post if not has_errors else None,
            success=not has_errors,
            errors=errors if errors else None,
            notification_removed=notification_removed,
        )
