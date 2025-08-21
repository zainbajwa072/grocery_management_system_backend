from django.contrib import admin
from .models import ItemType, Item

@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "item_type", "location", "price", "grocery", "added_by", "quantity_in_stock", "reorder_level")
    list_filter = ("location", "item_type", "grocery")
    search_fields = ("name", "sku")