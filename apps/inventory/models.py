"""
Capa de Datos - App: inventory
Registro de movimientos de stock para auditoria y trazabilidad.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN      = "in",      "Entrada"
        OUT     = "out",     "Salida"
        ADJUST  = "adjust",  "Ajuste"
        RESERVE = "reserve", "Reserva"
        RELEASE = "release", "Liberacion"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_movements")
    movement_type = models.CharField(max_length=10, choices=MovementType.choices)
    quantity = models.IntegerField("Cantidad")  # Puede ser negativo en salidas
    stock_before = models.PositiveIntegerField("Stock anterior")
    stock_after = models.PositiveIntegerField("Stock posterior")
    reference = models.CharField("Referencia", max_length=100, blank=True)  # Ej: numero de orden
    notes = models.TextField("Notas", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name}: {self.movement_type} {self.quantity}"
