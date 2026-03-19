"""
Capa de Negocio - App: cart
CartService: toda la logica del carrito en un solo lugar.
Las vistas solo llaman a este servicio, nunca acceden directamente a los modelos del carrito.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Cart, CartItem
from apps.products.models import Product


class CartService:
    """Servicio de negocio para operaciones del carrito."""

    @staticmethod
    def get_or_create_cart(request):
        """
        Obtiene o crea el carrito del usuario actual.
        - Si esta autenticado: carrito ligado al User.
        - Si es anonimo: carrito ligado a la sesion.
        """
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
        """
        Agrega un producto al carrito o incrementa su cantidad.
        Valida stock antes de agregar.
        """
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
        """Actualiza la cantidad de un item. Si quantity=0, lo elimina."""
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
        """Elimina un producto del carrito."""
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()

    @staticmethod
    def clear_cart(cart):
        """Vacia completamente el carrito."""
        cart.items.all().delete()

    @staticmethod
    @transaction.atomic
    def merge_anonymous_cart(user, session_key):
        """
        Fusiona el carrito anonimo con el del usuario autenticado.
        Se llama al hacer login.
        """
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
