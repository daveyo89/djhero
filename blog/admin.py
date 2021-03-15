from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from blog.models import Category, Post, PostImage, PostVideo, Introduction
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)


class PostImageAdmin(admin.StackedInline):
    model = PostImage


class PostVideoAdmin(admin.StackedInline):
    model = PostVideo


class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageAdmin, PostVideoAdmin]


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Introduction)
