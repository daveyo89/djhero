from django.contrib import admin
from blog.models import Category, Post, PostImage, PostVideo, Introduction


class PostImageAdmin(admin.StackedInline):
    model = PostImage


class PostVideoAdmin(admin.StackedInline):
    model = PostVideo


class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageAdmin, PostVideoAdmin]


# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Introduction)
