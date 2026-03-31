from django.db import models
from django.conf import settings
from apps.orders.models import Order


class Payment(models.Model):
    """
    Registra cada intento/transacción de pago asociado a una Order.
    Relación: orders_order 1:1 payments_payment
    """

    class Status(models.TextChoices):
        PENDING    = "pending",    "Pendiente"
        APPROVED   = "approved",   "Aprobado"
        REJECTED   = "rejected",   "Rechazado"
        CANCELLED  = "cancelled",  "Cancelado"
        IN_PROCESS = "in_process", "En proceso"
        REFUNDED   = "refunded",   "Reembolsado"

    class Provider(models.TextChoices):
        MERCADOPAGO = "mercadopago", "MercadoPago"
        STRIPE      = "stripe",      "Stripe"

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,   # Nunca borrar una orden con pago registrado
        related_name="payment",
    )
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        default=Provider.MERCADOPAGO,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # IDs que devuelve MercadoPago — útiles para rastrear en su dashboard
    preference_id  = models.CharField(max_length=255, blank=True)  # ID del checkout creado
    mp_payment_id  = models.CharField(max_length=255, blank=True)  # ID del pago aprobado
    merchant_order = models.CharField(max_length=255, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-created_at"]
        constraints = [
            # Un pago aprobado no puede tener monto <= 0
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="payment_amount_positive",
            )
        ]

    def __str__(self):
        return f"Pago #{self.id} — Orden #{self.order_id} [{self.status}]"

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED