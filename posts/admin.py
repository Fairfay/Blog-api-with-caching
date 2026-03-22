from django.contrib import admin

from posts.models import Post


class PostAdmin(admin.ModelAdmin):
    """Настройки отображения постов в административной панели."""


admin.site.register(Post, PostAdmin)
