from django.contrib.auth import get_user_model

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.template.loader import render_to_string
from django.utils.html import strip_tags

# from strawberry_django_jwt.shortcuts import get_token
from taggit.managers import TaggableManager
from autoslug import AutoSlugField

from django.conf import settings


class User(AbstractUser):
    pass


class UserStatus(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="status"
    )
    verified = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    secondary_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return "%s - status" % self.user

    def send(self, subject, template, context, recipient_list=None):
        _subject = render_to_string(subject, context).replace("\n", " ").strip()
        html_message = render_to_string(template, context)
        message = strip_tags(html_message)

        return send_mail(
            subject=_subject,
            from_email=settings.EMAIL_FROM,
            message=message,
            html_message=html_message,
            recipient_list=(
                recipient_list or [getattr(self.user, get_user_model().EMAIL_FIELD)]
            ),
            fail_silently=False,
        )

    def get_email_context(self, info, path, action, **kwargs):
        token = None
        # token = get_token(self.user, action, **kwargs)
        site = get_current_site(info.context)
        return {
            "user": self.user,
            "token": token,
            "port": info.context.get_port(),
            "site_name": site.name,
            "domain": site.domain,
            "protocol": "https" if info.context.is_secure() else "http",
            "path": path,
        }

    #
    # def send_activation_email(self, info, *args, **kwargs):
    #     # email_context = self.get_email_context(
    #     #     info, base.ACTIVATION_PATH_ON_EMAIL, TokenAction.ACTIVATION
    #     # )
    #     # template = base.EMAIL_TEMPLATE_ACTIVATION
    #     # subject = base.EMAIL_SUBJECT_ACTIVATION
    #     return self.send("subject", "template", "email_context", *args, **kwargs)


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
