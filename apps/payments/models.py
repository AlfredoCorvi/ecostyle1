"""
Capa de Datos - App: payments
Modelo: Payment
Relacion: Order 1:1 Payment
"""
from django.db import models
from apps.orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING   = "pending",   "Pendiente"
        APPROVED  = "approved",  "Aprobado"
        REJECTED  = "rejected",  "Rechazado"
        CANCELLED = "cancelled", "Cancelado"
        REFUNDED  = "refunded",  "Reembolsado"

    class Provider(models.TextChoices):
        MERCADOPAGO = "mercadopago", "MercadoPago"
        MANUAL      = "manual",      "Manual"

    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="payment")
    provider = models.CharField(max_length=20, choices=Provider.choices,
                                default=Provider.MERCADOPAGO)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # IDs externos del proveedor de pago
    external_id = models.CharField("ID externo", max_length=255, blank=True)
    preference_id = models.CharField("Preference ID", max_length=255, blank=True)

    amount = models.DecimalField("Monto", max_digits=10, decimal_places=2)
    currency = models.CharField("Moneda", max_length=3, default="MXN")

    # Metadata de la transaccion (guardada como JSON)
    raw_response = models.JSONField("Respuesta del proveedor", default=dict, blank=True)

    paid_at = models.DateTimeField("Fecha de pago", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pago {self.order.order_number} - {self.status}"
