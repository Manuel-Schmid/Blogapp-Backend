from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from blog.models import Category, Post, Comment, PostLike


class UserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password1', 'password2', 'username']


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email']


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'owner']


class PostLikeForm(ModelForm):
    class Meta:
        model = PostLike
        fields = ['post', 'user']


class CreateCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'text', 'post', 'owner']


class UpdateCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'text']
