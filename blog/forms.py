from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from blog.models import Category, Post, Comment, PostLike, AuthorRequest


class UserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["email", "password1", "password2", "username"]


class UpdateAccountForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name"]


class EmailChangeForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["email"]


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class CreateAuthorRequestForm(ModelForm):
    class Meta:
        model = AuthorRequest
        fields = ["user"]


class UpdateAuthorRequestForm(ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        data = kwargs.pop('data', {})
        data['status'] = data.get('status', {'value': None}).value
        kwargs['data'] = data
        super().__init__(*args, **kwargs)

    class Meta:
        model = AuthorRequest
        fields = ["date_closed", "status"]


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "category", "owner", "tags"]


class CreatePostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "image", "category", "owner", "tags"]


class PostLikeForm(ModelForm):
    class Meta:
        model = PostLike
        fields = ["post", "user"]


class CreateCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["title", "text", "post", "owner"]


class UpdateCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["title", "text"]
