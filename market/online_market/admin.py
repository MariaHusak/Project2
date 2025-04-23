from django.contrib import admin
from .models import User, BikeOrder
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.template.response import TemplateResponse
from .database import MongoDBConnection


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_verified', 'date_joined')
    list_filter = ('is_verified', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'email', 'password1', 'password2')}),
    )


class BikeOrderAdmin(admin.ModelAdmin):
    list_display = ('bike_type', 'frame', 'wheels', 'motor', 'get_user_list')
    search_fields = ('bike_type', 'frame', 'wheels')

    def get_user_list(self, obj):
        return ", ".join([user.username for user in obj.users.all()])
    get_user_list.short_description = 'Users'


admin.site.register(User, CustomUserAdmin)
admin.site.register(BikeOrder, BikeOrderAdmin)

