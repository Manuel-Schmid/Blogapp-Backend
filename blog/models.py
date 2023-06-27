from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware

from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils import timezone
from taggit.managers import TaggableManager
from autoslug import AutoSlugField
from django.conf import settings
from blog.api.inputs import Status
from blog.utils import TokenAction, get_token, get_token_payload


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='email address')


class UserProfile(models.Model):
    class Language(models.TextChoices):
        EN = 'ENGLISH'
        DE = 'GERMAN'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    dark_theme_active = models.BooleanField(default=False)
    comment_section_collapsed = models.BooleanField(default=False)
    related_posts_collapsed = models.BooleanField(default=False)
    language = models.CharField(max_length=20, choices=Language.choices, default=Language.EN)


class UserStatus(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_status')
    verified = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    is_author = models.BooleanField(default=False)
    secondary_email = models.EmailField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.user} - status'

    def send(self, subject_path: str, template_path: str, email_context: object) -> None:
        html_message = render_to_string(template_path, email_context)
        subject = render_to_string(subject_path, email_context)

        mail = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_FROM,
            to=[getattr(self.user, get_user_model().EMAIL_FIELD)],
        )
        mail.content_subtype = 'html'
        mail.send()

    def get_email_context(self, url_path: str, action: TokenAction, **kwargs) -> object:
        token = get_token(self.user, action, **kwargs)
        return {
            'user': self.user,
            'token': token,
            'port': settings.FRONTEND_PORT,
            'site_name': settings.FRONTEND_SITE_NAME,
            'protocol': settings.FRONTEND_PROTOCOL,
            'path': url_path,
            'frontend_domain': settings.FRONTEND_DOMAIN,
        }

    def send_activation_email(self) -> None:
        template_path = 'blog/email/activation_email.html'
        subject_path = 'blog/email/activation_subject.txt'
        email_context = self.get_email_context(settings.ACTIVATION_PATH_ON_EMAIL, TokenAction.ACTIVATION)
        self.send(subject_path, template_path, email_context)

    def send_password_reset_email(self) -> None:
        template_path = 'blog/email/password_reset_email.html'
        subject_path = 'blog/email/password_reset_subject.txt'
        email_context = self.get_email_context(settings.PASSWORD_RESET_PATH_ON_EMAIL, TokenAction.PASSWORD_RESET)
        self.send(subject_path, template_path, email_context)

    def send_email_change_email(self) -> None:
        template_path = 'blog/email/email_change_email.html'
        subject_path = 'blog/email/email_change_email.txt'
        email_context = self.get_email_context(settings.EMAIL_CHANGE_PATH_ON_EMAIL, TokenAction.EMAIL_CHANGE)
        self.send(subject_path, template_path, email_context)

    @staticmethod
    def verify(token: str) -> bool:
        payload = get_token_payload(token, TokenAction.ACTIVATION)
        if payload:
            user = User.objects.get(**payload)
            user_status = UserStatus.objects.get(user=user)
            if user_status.verified is False:
                user_status.verified = True
                user_status.save(update_fields=['verified'])
                return True
        return False


class AuthorRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING'
        REJECTED = 'REJECTED'
        ACCEPTED = 'ACCEPTED'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author_request')
    date_opened = models.DateTimeField('date opened', default=timezone.now)
    date_closed = models.DateTimeField('date closed', blank=True, null=True, default=None)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def __str__(self) -> str:
        return self.status

    @staticmethod
    def post_save(instance: 'AuthorRequest', **kwargs) -> None:
        post_save.disconnect(AuthorRequest.post_save, AuthorRequest, dispatch_uid='blog.models.AuthorRequest.post_save')
        instance.date_closed = None if instance.status == Status.PENDING.name else make_aware(datetime.now())
        instance.save()
        user_status = UserStatus.objects.get(user=instance.user)
        user_status.is_author = instance.status == Status.ACCEPTED.name
        user_status.save()
        post_save.connect(AuthorRequest.post_save, AuthorRequest, dispatch_uid='blog.models.AuthorRequest.post_save')


post_save.connect(AuthorRequest.post_save, AuthorRequest, dispatch_uid='blog.models.AuthorRequest.post_save')


def slugify(string: str) -> str:
    return string.replace(' ', '-').lower()


def post_slug_populate_from(value: object) -> object:
    return value.title


def category_slug_populate_from(value: object) -> object:
    return value.name


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(
        null=False,
        editable=False,
        unique=True,
        populate_from=category_slug_populate_from,
        slugify=slugify,
    )

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    class PostStatus(models.TextChoices):
        PUBLISHED = 'PUBLISHED'
        DRAFT = 'DRAFT'

    title = models.CharField(max_length=200, blank=False, null=False)
    slug = AutoSlugField(
        null=False,
        editable=False,
        unique=True,
        populate_from=post_slug_populate_from,
        slugify=slugify,
    )
    text = models.TextField()
    image = models.ImageField(upload_to='images', null=True)
    category = models.ForeignKey('blog.Category', related_name='posts', on_delete=models.CASCADE)
    owner = models.ForeignKey('blog.User', related_name='posts', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)
    status = models.CharField(max_length=20, choices=PostStatus.choices, default=PostStatus.DRAFT)
    tags = TaggableManager(blank=True)

    @property
    def image_url(self) -> str:
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def __str__(self) -> str:
        return self.title


class PostRelation(models.Model):
    main_post = models.ForeignKey('blog.Post', related_name='related_main_posts', on_delete=models.CASCADE)
    sub_post = models.ForeignKey('blog.Post', related_name='related_sub_posts', on_delete=models.CASCADE)
    creator = models.ForeignKey('blog.User', related_name='related_main_posts', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('main_post', 'sub_post')

    def clean(self) -> None:
        if self.main_post == self.sub_post:
            raise ValidationError('Main- and subpost must be different.')


class Subscription(models.Model):
    subscriber = models.ForeignKey('blog.User', related_name='subscriptions', on_delete=models.CASCADE)
    author = models.ForeignKey('blog.User', related_name='subscribers', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'author')

    def clean(self) -> None:
        if self.subscriber == self.author:
            raise ValidationError('Subscriber- and Author must be different.')


class Notification(models.Model):
    post = models.ForeignKey('blog.Post', related_name='notifications', on_delete=models.CASCADE)
    user = models.ForeignKey('blog.User', related_name='notifications', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')


class Comment(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    post = models.ForeignKey('blog.Post', related_name='comments', on_delete=models.CASCADE)
    owner = models.ForeignKey('blog.User', related_name='comments', on_delete=models.CASCADE)


class CommentLike(models.Model):
    comment = models.ForeignKey('blog.Comment', related_name='comment_likes', on_delete=models.CASCADE)
    user = models.ForeignKey('blog.User', related_name='comment_likes', on_delete=models.CASCADE)


class PostLike(models.Model):
    post = models.ForeignKey('blog.Post', related_name='post_likes', on_delete=models.CASCADE)
    user = models.ForeignKey('blog.User', related_name='post_likes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')
