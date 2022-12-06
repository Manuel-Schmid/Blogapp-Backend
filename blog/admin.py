from datetime import datetime
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from blog.api.inputs import Status
from blog.models import (
    Comment,
    User,
    Category,
    Post,
    CommentLike,
    PostLike,
    AuthorRequest,
    UserStatus,
)

admin.site.register(User, UserAdmin)
admin.site.register(Category)


class PostAdmin(admin.ModelAdmin):
    def image_tag(self, obj: object) -> str:
        return format_html('<img src="{}" width=150 height=150/>'.format(obj.image_url))

    image_tag.short_description = 'Image'

    list_display = ('title', 'date_created', 'category', 'owner', 'image_tag')


class AuthorRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_opened', 'date_closed', 'status')

    def save_model(self, request, obj, form, change):
        field = 'status'
        super().save_model(request, obj, form, change)
        if change and field in form.changed_data and form.cleaned_data.get(field):
            new_status = form.cleaned_data.get(field)
            if new_status == Status.PENDING.name:
                form.instance.date_closed = None
            else:
                form.instance.date_closed = datetime.now()
            form.save()

            user_status = UserStatus.objects.get(user=form.data.get('user'))
            user_status.is_author = new_status == Status.ACCEPTED.name
            user_status.save()


admin.site.register(Post, PostAdmin)
admin.site.register(AuthorRequest, AuthorRequestAdmin)

admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(PostLike)
