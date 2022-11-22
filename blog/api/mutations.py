from typing import Union

import strawberry
import strawberry_django_jwt.mutations as jwt_mutations
from strawberry.types import Info
from strawberry_django_jwt.decorators import login_required

from blog.api.auth_mutations import AuthMutations
from blog.api.decorators import author_permission_required
from blog.api.inputs import (
    PostInput,
    CategoryInput,
    CommentInput,
    PostLikeInput,
    AuthorRequestInput,
)
from blog.api.types import (
    Category as CategoryType,
    Post as PostType,
    Comment as CommentType,
    PostLike as PostLikeType,
    CreatePostType,
    AuthorRequestWrapperType,
)
from blog.models import Post, Category, Comment, PostLike, AuthorRequest
from blog.forms import (
    CategoryForm,
    PostForm,
    PostLikeForm,
    CreateCommentForm,
    UpdateCommentForm,
    CreatePostForm,
    CreateAuthorRequestForm,
    UpdateAuthorRequestForm,
)


@strawberry.type
class AuthMutation:
    token_auth = jwt_mutations.ObtainJSONWebToken.obtain
    verify_token = jwt_mutations.Verify.verify
    refresh_token = jwt_mutations.Refresh.refresh
    delete_token_cookie = jwt_mutations.DeleteJSONWebTokenCookie.delete_cookie
    delete_refresh_token_cookie = jwt_mutations.DeleteRefreshTokenCookie.delete_cookie

    register = AuthMutations.register
    resend_activation_email = AuthMutations.resend_activation_email
    verify_account = AuthMutations.verify_account
    password_change = AuthMutations.password_change
    email_change = AuthMutations.email_change
    send_password_reset_email = AuthMutations.send_password_reset_email
    send_email_change_email = AuthMutations.send_email_change_email
    password_reset = AuthMutations.password_reset
    update_account = AuthMutations.update_account


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
class AuthorRequestMutations:
    @login_required
    @strawberry.mutation
    def create_author_request(self, info: Info) -> AuthorRequestWrapperType:
        user = info.context.request.user
        form = CreateAuthorRequestForm(data={"user": user.id})
        if form.is_valid():
            author_request = form.save()
            return AuthorRequestWrapperType(
                author_request=author_request, success=True, errors=None
            )
        return AuthorRequestWrapperType(
            author_request=None, success=False, errors=form.errors.get_json_data()
        )

    @strawberry.mutation
    def update_author_request(
        self, author_request_input: AuthorRequestInput
    ) -> AuthorRequestWrapperType:
        author_request = AuthorRequest.objects.get(pk=author_request_input.id)
        form = UpdateAuthorRequestForm(
            instance=author_request, data=vars(author_request_input)
        )
        if form.is_valid():
            author_request = form.save()
            return AuthorRequestWrapperType(
                author_request=author_request, success=True, errors=None
            )
        return AuthorRequestWrapperType(
            author_request=None, success=False, errors=form.errors.get_json_data()
        )


@strawberry.type
class PostMutations:
    @login_required
    @author_permission_required
    @strawberry.mutation
    def create_post(self, info: Info, post_input: PostInput) -> CreatePostType:
        errors = {}
        has_errors = False
        post = None
        user = info.context.request.user
        post_input.owner = user.id
        files = info.context.request.FILES

        if len(files) != 1:
            has_errors = True
            errors.update({"file": "You must upload exactly one image file per post"})

        if not has_errors:
            form = CreatePostForm(data=vars(post_input), files={"image": files["1"]})

            if not form.is_valid():
                has_errors = True
                errors.update(form.errors.get_json_data())

            if not has_errors:
                post = form.save()

        return CreatePostType(
            post=post, success=not has_errors, errors=errors if errors else None
        )

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
    @login_required
    @strawberry.mutation
    def create_comment(
        self, info: Info, comment_input: CommentInput
    ) -> Union[CommentType, None]:
        user = info.context.request.user
        comment_input.owner = user.id
        form = CreateCommentForm(data=vars(comment_input))
        if form.is_valid():
            comment = form.save()
            return comment
        return None

    @login_required
    @strawberry.mutation
    def update_comment(
        self, info: Info, comment_input: CommentInput
    ) -> Union[CommentType, None]:
        user = info.context.request.user
        comment = Comment.objects.get(pk=comment_input.id)
        if comment.owner == user:
            form = UpdateCommentForm(instance=comment, data=vars(comment_input))
            if form.is_valid():
                comment = form.save()
                return comment
        return None

    @login_required
    @strawberry.mutation
    def delete_comment(self, info: Info, comment_id: strawberry.ID) -> bool:
        user = info.context.request.user
        Comment.objects.filter(pk=comment_id, owner_id=user.id).delete()
        return True


@strawberry.type
class PostLikeMutations:
    @login_required
    @strawberry.mutation
    def create_post_like(
        self, info: Info, post_like_input: PostLikeInput
    ) -> Union[PostLikeType, None]:
        user = info.context.request.user
        post_like_input.user = user.id
        form = PostLikeForm(data=vars(post_like_input))
        if form.is_valid():
            post_like = form.save()
            return post_like
        return None

    @strawberry.mutation
    @login_required
    def delete_post_like(self, info: Info, post_like_input: PostLikeInput) -> bool:
        user = info.context.request.user
        PostLike.objects.filter(post=post_like_input.post, user=user.id).delete()
        return True
