from django.db.models import Count

from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from blog.models import Category, Post, Comment, PostLike, User
from blog.api.types import User as UserType


class UserForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password1', 'password2', 'username']


class EmailChangeForm(forms.Form):
    error_messages = {
        'email_mismatch': "The two email addresses fields didn't match",
        'not_changed': "The email address is the same as the one already defined",
        'duplicate_email': "There is already an account using this email address",
    }

    new_email1 = forms.EmailField(
        label="New email address",
        widget=forms.EmailInput,
    )

    new_email2 = forms.EmailField(
        label="New email address confirmation",
        widget=forms.EmailInput,
    )

    def __init__(self, user: UserType, *args: any, **kwargs: any) -> None:
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_new_email1(self) -> str:
        old_email = self.user.email
        new_email1 = self.cleaned_data.get('new_email1')
        if new_email1 and old_email:
            if new_email1 == old_email:
                raise forms.ValidationError(
                    self.error_messages['not_changed'],
                    code='not_changed',
                )
            if len(User.objects.filter(email=new_email1).annotate(Count('id'))) > 0:
                raise forms.ValidationError(
                    self.error_messages['duplicate_email'],
                    code='duplicate_email',
                )
        return new_email1

    def clean_new_email2(self) -> str:
        new_email1 = self.cleaned_data.get('new_email1')
        new_email2 = self.cleaned_data.get('new_email2')
        if new_email1 and new_email2:
            if new_email1 != new_email2:
                raise forms.ValidationError(
                    self.error_messages['email_mismatch'],
                    code='email_mismatch',
                )
        return new_email2

    def save(self, commit: bool = True) -> UserType:
        email = self.cleaned_data["new_email1"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user


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
