"""
Capa de Negocio - App: payments
PaymentService: integracion con MercadoPago.
"""
import logging
import mercadopago
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .models import Payment
from apps.orders.models import Order

logger = logging.getLogger(__name__)


class PaymentService:
    """Servicio de pago con MercadoPago."""

    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    def create_preference(self, order):
        """
        Crea una preferencia de pago en MercadoPago.
        Retorna el init_point (URL de pago) y el preference_id.
        """
        items = []
        for item in order.items.all():
            items.append({
                "id": str(item.product.id),
                "title": item.product_name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "currency_id": "MXN",
            })

        preference_data = {
            "items": items,
            "payer": {
                "name": order.shipping_name,
                "email": order.shipping_email,
            },
            "external_reference": order.order_number,
            "notification_url": f"{settings.SITE_URL}/payments/webhook/",
            "back_urls": {
                "success": f"{settings.SITE_URL}/payments/success/",
                "failure": f"{settings.SITE_URL}/payments/failure/",
                "pending": f"{settings.SITE_URL}/payments/pending/",
            },
            "auto_return": "approved",
        }

        response = self.sdk.preference().create(preference_data)

        if response["status"] != 201:
            logger.error(f"MercadoPago error: {response}")
            raise Exception("No se pudo crear la preferencia de pago.")

        preference = response["response"]

        # Crear registro de pago en BD
        payment, _ = Payment.objects.update_or_create(
            order=order,
            defaults={
                "provider": Payment.Provider.MERCADOPAGO,
                "preference_id": preference["id"],
                "amount": order.total,
                "status": Payment.Status.PENDING,
            }
        )

        return {
            "preference_id": preference["id"],
            "init_point": preference["init_point"],
            "sandbox_init_point": preference.get("sandbox_init_point"),
        }

    @transaction.atomic
    def process_webhook(self, data):
        """
        Procesa notificaciones IPN de MercadoPago.
        Actualiza el estado del pago y de la orden.
        """
        topic = data.get("type")
        resource_id = data.get("data", {}).get("id")

        if topic != "payment" or not resource_id:
            return

        mp_payment = self.sdk.payment().get(resource_id)
        if mp_payment["status"] != 200:
            return

        payment_info = mp_payment["response"]
        order_number = payment_info.get("external_reference")
        mp_status = payment_info.get("status")

        try:
            order = Order.objects.get(order_number=order_number)
            payment = order.payment
        except (Order.DoesNotExist, Payment.DoesNotExist):
            logger.warning(f"Orden no encontrada: {order_number}")
            return

        # Mapeo de estados MercadoPago -> EcoStyle
        status_map = {
            "approved":    (Payment.Status.APPROVED,  Order.Status.CONFIRMED),
            "rejected":    (Payment.Status.REJECTED,  Order.Status.CANCELLED),
            "cancelled":   (Payment.Status.CANCELLED, Order.Status.CANCELLED),
            "refunded":    (Payment.Status.REFUNDED,  Order.Status.REFUNDED),
            "in_process":  (Payment.Status.PENDING,   Order.Status.PENDING),
        }

        payment_status, order_status = status_map.get(
            mp_status, (Payment.Status.PENDING, Order.Status.PENDING)
        )

        payment.status = payment_status
        payment.external_id = str(resource_id)
        payment.raw_response = payment_info
        if payment_status == Payment.Status.APPROVED:
            payment.paid_at = timezone.now()
        payment.save()

        order.status = order_status
        order.save()

        logger.info(f"Pago actualizado: {order_number} -> {payment_status}")
