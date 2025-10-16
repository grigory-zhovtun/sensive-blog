from django.contrib import admin
from blog.models import Post, Tag, Comment


# admin.site.register(Post)
# admin.site.register(Tag)
# admin.site.register(Comment)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_at']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'published_at']

# @admin.register(Admin)
# class AdminAdmin(admin.ModelAdmin):
#     list_display = ['name', 'telegram_id', 'is_active']
#     search_fields = ['name', 'telegram_id']