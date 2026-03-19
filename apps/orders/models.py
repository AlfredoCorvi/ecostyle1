"""
Capa de Datos - App: orders
Modelos: Order, OrderItem
Relacion: User 1:N Order  |  Order 1:N OrderItem  |  OrderItem N:1 Product
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from apps.products.models import Product
import uuid


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING    = "pending",    "Pendiente"
        CONFIRMED  = "confirmed",  "Confirmado"
        PROCESSING = "processing", "En proceso"
        SHIPPED    = "shipped",    "Enviado"
        DELIVERED  = "delivered",  "Entregado"
        CANCELLED  = "cancelled",  "Cancelado"
        REFUNDED   = "refunded",   "Reembolsado"

    # Numero de orden legible para el cliente
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Snapshot de la direccion en el momento del pedido (no FK, para preservar historial)
    shipping_name = models.CharField("Nombre", max_length=255)
    shipping_email = models.CharField("Email", max_length=255)
    shipping_phone = models.CharField("Telefono", max_length=20)
    shipping_address = models.CharField("Direccion", max_length=255)
    shipping_city = models.CharField("Ciudad", max_length=100)
    shipping_state = models.CharField("Estado", max_length=100)
    shipping_postal_code = models.CharField("Codigo Postal", max_length=10)
    shipping_country = models.CharField("Pais", max_length=100, default="Mexico")

    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,
                                   validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])

    notes = models.TextField("Notas del cliente", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Ordenes"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(check=models.Q(total__gte=0), name="order_total_non_negative"),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Genera numero legible tipo ECO-2024-XXXXXXXX
            short_uuid = str(uuid.uuid4()).replace("-", "")[:8].upper()
            self.order_number = f"ECO-{self.created_at.year if self.pk else '2024'}-{short_uuid}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Orden {self.order_number} - {self.user.email}"


class OrderItem(models.Model):
    """
    Snapshot del producto al momento de la compra.
    Guardamos precio y nombre para mantener historial aunque el producto cambie.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField("Nombre del producto", max_length=255)
    product_sku = models.CharField("SKU", max_length=100)
    unit_price = models.DecimalField("Precio unitario", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Cantidad")
    subtotal = models.DecimalField("Subtotal", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item de Orden"
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=1), name="orderitem_min_qty"),
        ]

    def save(self, *args, **kwargs):
        # Snapshot automatico del producto
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} @ ${self.unit_price}"
