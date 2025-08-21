from django.contrib import admin
from .models import DailyIncome

@admin.register(DailyIncome)
class DailyIncomeAdmin(admin.ModelAdmin):
    list_display = ("grocery", "date", "formatted_amount", "recorded_by")  
    list_filter = ("grocery", "date", "recorded_by")  
    search_fields = ("grocery__name", "notes", "recorded_by__username")  
    ordering = ("-date",)
