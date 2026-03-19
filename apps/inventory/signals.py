"""
Capa de Negocio - App: inventory
Signals para control automatico de stock al confirmar/cancelar ordenes.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import Order
from apps.products.models import Product
from .models import StockMovement

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def handle_order_stock(sender, instance, created, **kwargs):
    """
    Reduce stock cuando una orden es CONFIRMADA.
    Libera stock si la orden es CANCELADA (y fue confirmada antes).
    """
    if instance.status == Order.Status.CONFIRMED:
        _reduce_stock(instance)
    elif instance.status == Order.Status.CANCELLED:
        _restore_stock(instance)


def _reduce_stock(order):
    """Descuenta stock por cada item de la orden."""
    for item in order.items.select_related("product").all():
        product = Product.objects.select_for_update().get(pk=item.product_id)
        if product.stock < item.quantity:
            logger.error(
                f"Stock insuficiente para {product.name} en orden {order.order_number}"
            )
            continue

        stock_before = product.stock
        product.stock -= item.quantity
        product.save(update_fields=["stock"])

        StockMovement.objects.create(
            product=product,
            movement_type=StockMovement.MovementType.OUT,
            quantity=-item.quantity,
            stock_before=stock_before,
            stock_after=product.stock,
            reference=order.order_number,
            notes=f"Venta confirmada - Orden {order.order_number}",
        )
        logger.info(f"Stock reducido: {product.name} {stock_before} -> {product.stock}")


def _restore_stock(order):
    """Restaura stock al cancelar una orden (solo si fue confirmada)."""
    movements = StockMovement.objects.filter(
        reference=order.order_number,
        movement_type=StockMovement.MovementType.OUT
    )
    for movement in movements:
        product = Product.objects.select_for_update().get(pk=movement.product_id)
        stock_before = product.stock
        product.stock += abs(movement.quantity)
        product.save(update_fields=["stock"])

        StockMovement.objects.create(
            product=product,
            movement_type=StockMovement.MovementType.RELEASE,
            quantity=abs(movement.quantity),
            stock_before=stock_before,
            stock_after=product.stock,
            reference=order.order_number,
            notes=f"Orden cancelada - Liberacion de stock",
        )
        logger.info(f"Stock restaurado: {product.name} {stock_before} -> {product.stock}")
