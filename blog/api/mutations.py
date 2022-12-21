from typing import Union, Optional, Any

import strawberry
import strawberry_django_jwt.mutations as jwt_mutations
from strawberry.types import Info
from strawberry_django_jwt import exceptions
from strawberry_django_jwt.decorators import (
    login_required,
    dispose_extra_kwargs,
    superuser_required,
    setup_jwt_cookie,
    csrf_rotation,
    refresh_expiration,
)
from strawberry_django_jwt.mixins import RefreshMixin
from strawberry_django_jwt.settings import jwt_settings
from strawberry_django_jwt.object_types import TokenDataType, TokenPayloadType
from strawberry_django_jwt.refresh_token.decorators import ensure_refresh_token
from strawberry_django_jwt.refresh_token.object_types import RefreshedTokenType
from strawberry_django_jwt.refresh_token.shortcuts import (
    get_refresh_token,
    create_refresh_token,
    refresh_token_lazy_async,
    refresh_token_lazy,
)
from django.utils.translation import gettext as _
from strawberry_django_jwt.utils import get_context
from strawberry_django_jwt.refresh_token import signals as refresh_signals
from blog.api.auth_mutations import AuthMutations
from blog.api.decorators import author_permission_required, token_auth
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


class RefreshToken(jwt_mutations.Refresh):
    @staticmethod
    @setup_jwt_cookie
    @csrf_rotation
    @refresh_expiration
    @ensure_refresh_token
    def _refresh(
        self: Any, info: Info, refresh_token: Optional[str], _is_async: Optional[bool] = False
    ) -> RefreshedTokenType:
        context = get_context(info)
        old_refresh_token = get_refresh_token(refresh_token, context)

        if old_refresh_token.is_expired(context):
            raise exceptions.JSONWebTokenError(_('Refresh token is expired'))

        payload = jwt_settings.JWT_PAYLOAD_HANDLER(
            old_refresh_token.user,
            context,
        )
        token = jwt_settings.JWT_ENCODE_HANDLER(payload, context)

        if hasattr(context, 'jwt_cookie'):
            context.jwt_refresh_token = create_refresh_token(
                old_refresh_token.user,
                old_refresh_token,
            )
            new_refresh_token = context.jwt_refresh_token.get_token()
        else:
            new_refresh_token = (refresh_token_lazy_async if _is_async else refresh_token_lazy)(
                old_refresh_token.user,
                old_refresh_token,
            )

        refresh_signals.refresh_token_rotated.send(
            sender=RefreshMixin,
            request=context,
            refresh_token=old_refresh_token,
            refresh_token_issued=new_refresh_token,
        )
        return RefreshedTokenType(payload=payload, token=token, refresh_token=new_refresh_token, refresh_expires_in=0)

    @strawberry.mutation
    def refresh(self, info: Info, refresh_token: Optional[str] = None) -> RefreshedTokenType:
        return RefreshToken._refresh(self, info=info, refresh_token=refresh_token)


@strawberry.type
class ObtainJSONWebToken(jwt_mutations.ObtainJSONWebToken):
    @strawberry.mutation
    @token_auth  # Custom decorator based on the strawberry decorator with the same name
    @dispose_extra_kwargs
    def token_auth(self, info: Info) -> TokenDataType:
        return TokenDataType(payload=TokenPayloadType())


@strawberry.type
class AuthMutation:
    verify_token = jwt_mutations.Verify.verify
    refresh_token = RefreshToken.refresh
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
    def create_category(self, category_input: CategoryInput) -> Union[CategoryType, None]:
        form = CategoryForm(data=vars(category_input))
        if form.is_valid():
            category = form.save()
            return category
        return None

    @strawberry.mutation
    def update_category(self, category_input: CategoryInput) -> Union[CategoryType, None]:
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
        form = CreateAuthorRequestForm(data={'user': user.id})
        if form.is_valid():
            author_request = form.save()
            return AuthorRequestWrapperType(author_request=author_request, success=True, errors=None)
        return AuthorRequestWrapperType(author_request=None, success=False, errors=form.errors.get_json_data())

    @superuser_required
    @strawberry.mutation
    def update_author_request(self, author_request_input: AuthorRequestInput) -> AuthorRequestWrapperType:
        author_request = AuthorRequest.objects.get(user=author_request_input.user)
        form = UpdateAuthorRequestForm(instance=author_request, data=vars(author_request_input))
        if form.is_valid():
            author_request = form.save()
            return AuthorRequestWrapperType(author_request=author_request, success=True, errors=None)
        return AuthorRequestWrapperType(author_request=None, success=False, errors=form.errors.get_json_data())


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
            errors.update({'file': 'You must upload exactly one image file per post'})

        if not has_errors:
            form = CreatePostForm(data=vars(post_input), files={'image': files['1']})

            if not form.is_valid():
                has_errors = True
                errors.update(form.errors.get_json_data())

            if not has_errors:
                post = form.save()

        return CreatePostType(post=post, success=not has_errors, errors=errors if errors else None)

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
    def create_comment(self, info: Info, comment_input: CommentInput) -> Union[CommentType, None]:
        user = info.context.request.user
        comment_input.owner = user.id
        form = CreateCommentForm(data=vars(comment_input))
        if form.is_valid():
            comment = form.save()
            return comment
        return None

    @login_required
    @strawberry.mutation
    def update_comment(self, info: Info, comment_input: CommentInput) -> Union[CommentType, None]:
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
    def create_post_like(self, info: Info, post_like_input: PostLikeInput) -> Union[PostLikeType, None]:
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
