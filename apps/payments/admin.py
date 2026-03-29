from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order", "provider", "status", "amount", "created_at"]
    list_filter = ["provider", "status"]
    readonly_fields = ["preference_id", "mp_payment_id", "merchant_order", "created_at", "updated_at"]