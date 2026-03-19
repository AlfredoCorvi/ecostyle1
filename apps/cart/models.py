"""
Capa de Datos - App: cart
Modelos: Cart, CartItem
Relacion: User 1:1 Cart  |  Cart 1:N CartItem  |  CartItem N:1 Product
"""
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class Cart(models.Model):
    """Carrito de compras. Un usuario tiene exactamente un carrito activo."""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart", null=True, blank=True
    )
    # Para usuarios anonimos usamos session_key
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Carrito"
        constraints = [
            # O tiene usuario O tiene session_key, nunca ambos nulos
            models.CheckConstraint(
                check=models.Q(user__isnull=False) | models.Q(session_key__isnull=False),
                name="cart_owner_required"
            )
        ]

    def __str__(self):
        owner = self.user.email if self.user else f"Sesion {self.session_key}"
        return f"Carrito de {owner}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def is_empty(self):
        return not self.items.exists()


class CartItem(models.Model):
    """Item dentro del carrito."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Cantidad", default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item del Carrito"
        unique_together = [("cart", "product")]  # Sin duplicados por producto
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=1), name="cartitem_min_qty")
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity
