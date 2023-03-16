from typing import Any

from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from blog.models import (
    Category,
    Post,
    Comment,
    PostLike,
    AuthorRequest,
    PostRelation,
    UserProfile,
    Subscription,
    Notification,
)


class UserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password1', 'password2', 'username']


class UpdateAccountForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']


class EmailChangeForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email']


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class CreateAuthorRequestForm(ModelForm):
    class Meta:
        model = AuthorRequest
        fields = ['user']


class UpdateAuthorRequestForm(ModelForm):
    def __init__(self, *args: Any, **kwargs) -> None:
        data = kwargs.pop('data', {})
        data['status'] = data.get('status', {'value': None}).value
        kwargs['data'] = data
        super().__init__(*args, **kwargs)

    class Meta:
        model = AuthorRequest
        fields = ['date_closed', 'status']


class UpdatePostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image', 'category', 'owner', 'tags']

    def __init__(self, *args: Any, **kwargs) -> None:
        super(UpdatePostForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False


class UpdatePostStatusForm(ModelForm):
    def __init__(self, *args: Any, **kwargs) -> None:
        data = kwargs.pop('data', {})
        data['status'] = data.get('status', {'value': None}).value
        kwargs['data'] = data
        super().__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ['status']


class CreatePostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image', 'category', 'owner', 'tags']


class PostLikeForm(ModelForm):
    class Meta:
        model = PostLike
        fields = ['post', 'user']


class PostRelationForm(ModelForm):
    class Meta:
        model = PostRelation
        fields = ['main_post', 'sub_post', 'creator']


class SubscriptionForm(ModelForm):
    class Meta:
        model = Subscription
        fields = ['subscriber', 'author']


class NotificationForm(ModelForm):
    class Meta:
        model = Notification
        fields = ['post', 'user']


class CreateCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'text', 'post', 'owner']


class UpdateCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'text']


class UserProfileForm(ModelForm):
    def __init__(self, *args: Any, **kwargs) -> None:
        data = kwargs.pop('data', {})
        data['language'] = data.get('language', {'value': None}).value
        kwargs['data'] = data
        super().__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ['dark_theme_active', 'comment_section_collapsed', 'related_posts_collapsed', 'language']
