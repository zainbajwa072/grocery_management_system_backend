from django.contrib import admin
from .models import Grocery


@admin.register(Grocery)
class GroceryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "location",
        "created_by",
        "supplier_count",
        "item_count",
        "created_at",
        "updated_at",
    )
    list_filter = ("location", "created_by", "created_at")
    search_fields = ("name", "location", "created_by__email")
    readonly_fields = ("supplier_count", "item_count", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": ("name", "location", "created_by")
        }),
        ("Statistics", {
            "fields": ("supplier_count", "item_count"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )
