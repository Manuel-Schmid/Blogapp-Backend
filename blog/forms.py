from django.forms import ModelForm
from blog.models import User, Category, Post, Comment, PostLike


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'first_name', 'last_name']


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
