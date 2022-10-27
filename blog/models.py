from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from taggit.managers import TaggableManager
from autoslug import AutoSlugField
from django.conf import settings
from blog.utils import TokenAction, get_token, get_token_payload


class User(AbstractUser):
    pass


class UserStatus(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='status'
    )
    verified = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    secondary_email = models.EmailField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.user} - status'

    def send(self, subject_path: str, template_path: str, email_context: object) -> None:
        html_message = render_to_string(template_path, email_context)
        subject = open(subject_path, 'r').read()

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
            'frontend_domain': settings.FRONTEND_DOMAIN
        }

    def send_activation_email(self) -> None:
        template_path = 'email/activation_email.html'
        subject_path = 'blog/templates/blog/email/activation_subject.txt'
        email_context = self.get_email_context(settings.ACTIVATION_PATH_ON_EMAIL, TokenAction.ACTIVATION)
        self.send(subject_path, template_path, email_context)

    @staticmethod
    def verify(token: str) -> bool:
        payload = get_token_payload(
            token, TokenAction.ACTIVATION
        )
        if payload:
            user = User._default_manager.get(**payload)
            user_status = UserStatus.objects.get(user=user)
            if user_status.verified is False:
                user_status.verified = True
                user_status.save(update_fields=['verified'])
                return True
        return False


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
    category = models.ForeignKey(
        'blog.Category', related_name='posts', on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        'blog.User', related_name='posts', on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    @property
    def image_url(self) -> str:
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    post = models.ForeignKey(
        'blog.Post', related_name='comments', on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        'blog.User', related_name='comments', on_delete=models.CASCADE
    )


class CommentLike(models.Model):
    comment = models.ForeignKey(
        'blog.Comment', related_name='comment_likes', on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        'blog.User', related_name='comment_likes', on_delete=models.CASCADE
    )


class PostLike(models.Model):
    post = models.ForeignKey(
        'blog.Post', related_name='post_likes', on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        'blog.User', related_name='post_likes', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('post', 'user')
