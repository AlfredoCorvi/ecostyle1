from django.contrib import admin
from .models import StockMovement


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["product", "movement_type", "quantity", "stock_before", "stock_after", "reference", "created_at"]
    list_filter = ["movement_type"]
    readonly_fields = ["created_at"]
