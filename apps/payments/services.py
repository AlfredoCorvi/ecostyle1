import mercadopago
import logging
from django.conf import settings
from apps.orders.models import Order
from apps.payments.models import Payment

logger = logging.getLogger(__name__)


class PaymentService:

    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    def create_preference(self, order: Order, request) -> dict:

        items = []
        for item in order.items.select_related("product").all():
            items.append({
                "id": str(item.product.id),
                "title": item.product.name,
                "description": item.product.description[:255] if item.product.description else "",
                "category_id": "fashion",
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "currency_id": "MXN",
            })

        preference_data = {
            "items": items,
            "payer": {
                "name": order.user.first_name,
                "surname": order.user.last_name,
                "email": order.user.email,
            },
            "back_urls": {
                "success": f"http://127.0.0.1:8000/payments/success/?order_id={order.id}",
                "failure": f"http://127.0.0.1:8000/payments/failure/?order_id={order.id}",
                "pending": f"http://127.0.0.1:8000/payments/pending/?order_id={order.id}",
            },
            "external_reference": str(order.id),
            "statement_descriptor": "ECOSTYLE",
        }

        logger.info(f"Creando preference MP para orden #{order.id}")
        response = self.sdk.preference().create(preference_data)

        if response["status"] not in [200, 201]:
            logger.error(f"Error MP al crear preference: {response}")
            raise Exception(f"MercadoPago error: {response.get('response', {})}")

        preference = response["response"]

        payment, _ = Payment.objects.update_or_create(
            order=order,
            defaults={
                "provider": Payment.Provider.MERCADOPAGO,
                "status": Payment.Status.PENDING,
                "preference_id": preference["id"],
                "amount": order.total,
            },
        )

        checkout_url = preference.get("sandbox_init_point") or preference["init_point"]

        return {
            "preference_id": preference["id"],
            "init_point": checkout_url,
            "payment": payment,
        }

    def process_webhook(self, data: dict) -> Payment | None:
        topic = data.get("type") or data.get("topic")
        if topic != "payment":
            return None

        mp_payment_id = str(data.get("data", {}).get("id") or data.get("id", ""))
        if not mp_payment_id:
            return None

        response = self.sdk.payment().get(mp_payment_id)
        if response["status"] != 200:
            logger.error(f"No se pudo obtener pago MP {mp_payment_id}: {response}")
            return None

        mp_data = response["response"]
        order_id = mp_data.get("external_reference")
        status = mp_data.get("status", "pending")

        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.status = status
            payment.mp_payment_id = mp_payment_id
            payment.save(update_fields=["status", "mp_payment_id", "updated_at"])
            logger.info(f"Pago #{payment.id} actualizado a '{status}' vía webhook")
            return payment
        except Payment.DoesNotExist:
            logger.error(f"Webhook MP: No existe pago para orden #{order_id}")
            return None