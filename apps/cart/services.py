"""
Capa de Negocio - App: cart
CartService: toda la logica del carrito en un solo lugar.
"""
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Cart, CartItem
from apps.products.models import Product


# ── Constantes de negocio ─────────────────────────────────────────
FREE_SHIPPING_THRESHOLD = Decimal('999.00')   # envío gratis sobre este monto
SHIPPING_COST           = Decimal('99.00')    # costo fijo de envío
TAX_RATE                = Decimal('0.16')     # IVA 16%


class CartService:
    """Servicio de negocio para operaciones del carrito."""

    # ── Métodos existentes (sin cambios) ─────────────────────────

    @staticmethod
    def get_or_create_cart(request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            cart, _ = Cart.objects.get_or_create(
                session_key=request.session.session_key
            )
        return cart

    @staticmethod
    @transaction.atomic
    def add_item(cart, product_id, quantity=1):
        product = Product.objects.select_for_update().get(pk=product_id, is_active=True)

        if quantity < 1:
            raise ValidationError("La cantidad debe ser al menos 1.")
        if product.stock < quantity:
            raise ValidationError(f"Solo hay {product.stock} unidades disponibles.")

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            new_qty = item.quantity + quantity
            if product.stock < new_qty:
                raise ValidationError(f"Solo hay {product.stock} unidades disponibles.")
            item.quantity = new_qty
            item.save()

        return item

    @staticmethod
    @transaction.atomic
    def update_quantity(cart, product_id, quantity):
        if quantity == 0:
            CartItem.objects.filter(cart=cart, product_id=product_id).delete()
            return None

        product = Product.objects.select_for_update().get(pk=product_id)
        if product.stock < quantity:
            raise ValidationError(f"Solo hay {product.stock} unidades disponibles.")

        item = CartItem.objects.get(cart=cart, product_id=product_id)
        item.quantity = quantity
        item.save()
        return item

    @staticmethod
    def remove_item(cart, product_id):
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()

    @staticmethod
    def clear_cart(cart):
        cart.items.all().delete()

    @staticmethod
    @transaction.atomic
    def merge_anonymous_cart(user, session_key):
        try:
            anon_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
        except Cart.DoesNotExist:
            return

        user_cart, _ = Cart.objects.get_or_create(user=user)

        for anon_item in anon_cart.items.all():
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart, product=anon_item.product
            )
            if not created:
                user_item.quantity += anon_item.quantity
                user_item.save()

        anon_cart.delete()

    # ── Métodos de cálculo de totales (nuevos) ────────────────────

    @staticmethod
    def get_subtotal(cart):
        """Suma precio × cantidad de todos los items."""
        items = cart.items.select_related('product').all()
        return sum(item.product.price * item.quantity for item in items)

    @staticmethod
    def get_tax(cart):
        """IVA sobre el subtotal."""
        return (CartService.get_subtotal(cart) * TAX_RATE).quantize(Decimal('0.01'))

    @staticmethod
    def get_shipping(cart):
        """Envío gratis si supera el umbral, sino costo fijo."""
        subtotal = CartService.get_subtotal(cart)
        return Decimal('0.00') if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST

    @staticmethod
    def get_total(cart):
        """Total final: subtotal + IVA + envío."""
        return (
            CartService.get_subtotal(cart)
            + CartService.get_tax(cart)
            + CartService.get_shipping(cart)
        )

    @staticmethod
    def get_totals(cart):
        """
        Devuelve todos los totales en un solo dict.
        Útil para vistas y respuestas JSON.
        """
        subtotal  = CartService.get_subtotal(cart)
        tax       = (subtotal * TAX_RATE).quantize(Decimal('0.01'))
        shipping  = Decimal('0.00') if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST
        total     = subtotal + tax + shipping

        return {
            'subtotal':         subtotal,
            'tax':              tax,
            'shipping':         shipping,
            'total':            total,
            'free_shipping':    subtotal >= FREE_SHIPPING_THRESHOLD,
            'free_shipping_remaining': max(FREE_SHIPPING_THRESHOLD - subtotal, Decimal('0.00')),
        }

    @staticmethod
    def get_line_total(item):
        """Total de una línea individual: precio × cantidad."""
        return (item.product.price * item.quantity).quantize(Decimal('0.01'))