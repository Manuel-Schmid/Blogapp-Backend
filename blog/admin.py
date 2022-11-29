from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from blog.models import (
    Comment,
    User,
    Category,
    Post,
    CommentLike,
    PostLike,
    AuthorRequest,
)

admin.site.register(User, UserAdmin)
admin.site.register(Category)


class PostAdmin(admin.ModelAdmin):
    def image_tag(self, obj: object) -> str:
        return format_html('<img src="{}" width=150 height=150/>'.format(obj.image_url))

    image_tag.short_description = 'Image'

    list_display = ('title', 'date_created', 'category', 'owner', 'image_tag')


admin.site.register(Post, PostAdmin)
admin.site.register(AuthorRequest)

admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(PostLike)
