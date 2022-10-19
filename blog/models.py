from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from autoslug import AutoSlugField


class User(AbstractUser):
    pass


def slugify(value):
    return value.replace(' ', '-').lower()


def post_slug_populate_from(value):
    return value.title


def category_slug_populate_from(value):
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

    def __str__(self):
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
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def __str__(self):
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
