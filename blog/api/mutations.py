from typing import Union

import strawberry
import strawberry_django_jwt.mutations as jwt_mutations
from strawberry.types import Info

from blog.api.auth_mutations import AuthMutations
from blog.api.inputs import PostInput, CategoryInput, CommentInput, PostLikeInput
from blog.api.types import (
    Category as CategoryType,
    Post as PostType,
    Comment as CommentType,
    PostLike as PostLikeType,
    User as UserType,
)
from blog.models import Post, Category, Comment, PostLike, User
from blog.forms import (
    CategoryForm,
    PostForm,
    PostLikeForm,
    CreateCommentForm,
    UpdateCommentForm,
)


@strawberry.type
class AuthMutation:
    token_auth = jwt_mutations.ObtainJSONWebToken.obtain
    verify_token = jwt_mutations.Verify.verify
    refresh_token = jwt_mutations.Refresh.refresh
    delete_token_cookie = jwt_mutations.DeleteJSONWebTokenCookie.delete_cookie
    delete_refresh_token_cookie = jwt_mutations.DeleteRefreshTokenCookie.delete_cookie

    register = AuthMutations.register
    verify_account = AuthMutations.verify_account


@strawberry.type
class UserMutations:
    @strawberry.mutation
    def update_user_email(self, info: Info, new_email: str) -> Union[UserType, None]:
        user = info.context.request.user
        if user.is_authenticated:
            new_user = User.objects.get(pk=user.id)
            new_user.email = new_email
            new_user.save()
            return new_user
        return None


@strawberry.type
class CategoryMutations:
    @strawberry.mutation
    def create_category(
        self, category_input: CategoryInput
    ) -> Union[CategoryType, None]:
        form = CategoryForm(data=vars(category_input))
        if form.is_valid():
            category = form.save()
            return category
        return None

    @strawberry.mutation
    def update_category(
        self, category_input: CategoryInput
    ) -> Union[CategoryType, None]:
        category = Category.objects.get(pk=category_input.id)
        form = CategoryForm(instance=category, data=vars(category_input))
        if form.is_valid():
            category = form.save()
            return category
        return None


@strawberry.type
class PostMutations:
    @strawberry.mutation
    def create_post(self, info: Info, post_input: PostInput) -> Union[PostType, None]:
        user = info.context.request.user
        if user.is_authenticated:
            post_input.owner = user.id
            form = PostForm(data=vars(post_input))
            if form.is_valid():
                post = form.save()
                return post
        return None

    @strawberry.mutation
    def update_post(self, post_input: PostInput) -> Union[PostType, None]:
        post = Post.objects.get(slug=post_input.slug)
        form = PostForm(instance=post, data=vars(post_input))
        if form.is_valid():
            post = form.save()
            return post
        return None


@strawberry.type
class CommentMutations:
    @strawberry.mutation
    def create_comment(
        self, info: Info, comment_input: CommentInput
    ) -> Union[CommentType, None]:
        user = info.context.request.user
        if user.is_authenticated:
            comment_input.owner = user.id
            form = CreateCommentForm(data=vars(comment_input))
            if form.is_valid():
                comment = form.save()
                return comment
        return None

    @strawberry.mutation
    def update_comment(self, comment_input: CommentInput) -> Union[CommentType, None]:
        comment = Comment.objects.get(pk=comment_input.id)
        form = UpdateCommentForm(instance=comment, data=vars(comment_input))
        if form.is_valid():
            comment = form.save()
            return comment
        return None

    @strawberry.mutation
    def delete_comment(self, info: Info, comment_id: strawberry.ID) -> bool:
        user = info.context.request.user
        if user.is_authenticated:
            Comment.objects.filter(pk=comment_id, owner_id=user.id).delete()
        return True


@strawberry.type
class PostLikeMutations:
    @strawberry.mutation
    def create_post_like(
        self, info: Info, post_like_input: PostLikeInput
    ) -> Union[PostLikeType, None]:
        user = info.context.request.user
        if user.is_authenticated:
            post_like_input.user = user.id
            form = PostLikeForm(data=vars(post_like_input))
            if form.is_valid():
                post_like = form.save()
                return post_like
        return None

    @strawberry.mutation
    def delete_post_like(self, info: Info, post_like_input: PostLikeInput) -> bool:
        user = info.context.request.user
        if user.is_authenticated:
            PostLike.objects.filter(post=post_like_input.post, user=user.id).delete()
        return True
