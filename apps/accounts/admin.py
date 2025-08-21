from django.contrib import admin
from .models import User, AdminProfile, SupplierProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username", "user_type", "is_active", "is_staff")
    list_filter = ("user_type", "is_active", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name")


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department", "phone_number")
    search_fields = ("user__email", "user__username", "department")


@admin.register(SupplierProfile)
class SupplierProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "assigned_grocery", "phone_number", "hire_date")
    list_filter = ("assigned_grocery",)
    search_fields = ("user__email", "user__username", "phone_number")
