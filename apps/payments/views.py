import json
import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages

from apps.orders.models import Order
from .services import PaymentService
from .models import Payment

logger = logging.getLogger(__name__)


class CreatePaymentView(LoginRequiredMixin, View):

    def post(self, request, order_id):
        print(f">>> 1. POST recibido para orden {order_id}")
        order = get_object_or_404(Order, id=order_id, user=request.user)
        print(f">>> 2. Orden encontrada: {order.id}")

        # Verifica si is_paid existe en el modelo
        try:
            print(f">>> 3. is_paid: {order.is_paid}")
        except AttributeError:
            print(">>> 3. ERROR: is_paid no existe en el modelo Order")

        try:
            service = PaymentService()
            print(">>> 4. Llamando a MercadoPago API...")
            result = service.create_preference(order, request)
            print(f">>> 5. Preference creada: {result['preference_id']}")
            return redirect(result["init_point"])

        except Exception as e:
            print(f">>> ERROR en {type(e).__name__}: {e}")
            messages.error(request, "Hubo un problema al procesar el pago.")
            return redirect("cart:detail")


class PaymentSuccessView(LoginRequiredMixin, View):
    """MP redirige aquí cuando el pago fue APROBADO."""

    def get(self, request):
        order_id = request.GET.get("order_id")
        # MP también envía: payment_id, status, merchant_order_id en los query params
        mp_payment_id = request.GET.get("payment_id")
        status = request.GET.get("status")

        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Actualizamos el pago localmente con lo que MP nos envía por URL
        # (el webhook también lo actualiza, esto es doble seguridad)
        if mp_payment_id and status == "approved":
            Payment.objects.filter(order=order).update(
                status=Payment.Status.APPROVED,
                mp_payment_id=mp_payment_id,
            )
            # Marcar la orden como pagada
            order.status = Order.Status.CONFIRMED
            order.save(update_fields=["status"])

        return render(request, "payments/success.html", {"order": order})


class PaymentFailureView(LoginRequiredMixin, View):
    """MP redirige aquí cuando el pago fue RECHAZADO."""

    def get(self, request):
        order_id = request.GET.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return render(request, "payments/failure.html", {"order": order})


class PaymentPendingView(LoginRequiredMixin, View):
    """MP redirige aquí cuando el pago queda EN PROCESO (ej: transferencia bancaria)."""

    def get(self, request):
        order_id = request.GET.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return render(request, "payments/pending.html", {"order": order})


@method_decorator(csrf_exempt, name="dispatch")  # MP no envía CSRF token
class PaymentWebhookView(View):
    """
    Endpoint IPN/Webhook. MercadoPago notifica aquí cada cambio de estado.
    POST /payments/webhook/
    Debe ser accesible desde internet (usa ngrok en desarrollo).
    """

    def post(self, request):
        try:
            # MP puede enviar JSON en el body O parámetros en la URL
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.GET.dict()

            service = PaymentService()
            service.process_webhook(data)

        except Exception as e:
            logger.error(f"Error en webhook MP: {e}")

        # Siempre responder 200 — si MP no recibe 200, reintenta el webhook
        return HttpResponse(status=200)
    
# apps/payments/views.py
from django.conf import settings

class PaymentCheckoutView(LoginRequiredMixin, View):
    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        try:
            service = PaymentService()
            result = service.create_preference(order, request)
            return redirect(result["init_point"])  # ← redirige directo
        except Exception as e:
            logger.error(f"Error al crear preference: {e}")
            messages.error(request, "Error al conectar con MercadoPago.")
            return redirect("cart:detail")