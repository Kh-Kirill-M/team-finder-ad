from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-id",)
    list_display = ("id", "email", "name", "surname", "phone", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "name", "surname", "phone")
    filter_horizontal = ("favorites", "groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личные данные", {
            "fields": ("name", "surname", "avatar", "phone", "github_url", "about"),
        }),
        ("Избранное", {"fields": ("favorites",)}),
        ("Права", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Служебное", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "surname", "phone", "password1", "password2"),
        }),
    )
    readonly_fields = ("date_joined", "last_login")
