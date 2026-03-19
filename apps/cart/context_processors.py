"""
Context processor: inyecta el resumen del carrito en todos los templates.
Esto permite mostrar el contador del carrito en el navbar globalmente.
"""
from .services import CartService


def cart_summary(request):
    cart = CartService.get_or_create_cart(request)
    return {
        "cart": cart,
        "cart_total_items": cart.total_items,
        "cart_subtotal": cart.subtotal,
    }
