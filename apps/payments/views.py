import json
import logging
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.orders.models import Order
from .services import PaymentService

logger = logging.getLogger(__name__)


class PaymentCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "payments/checkout.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order = Order.objects.get(
            order_number=self.kwargs["order_number"],
            user=self.request.user
        )
        service = PaymentService()
        preference = service.create_preference(order)
        ctx["order"] = order
        ctx["preference_id"] = preference["preference_id"]
        ctx["mp_public_key"] = __import__("django.conf", fromlist=["settings"]).settings.MERCADOPAGO_PUBLIC_KEY
        return ctx


class PaymentSuccessView(TemplateView):
    template_name = "payments/success.html"


class PaymentFailureView(TemplateView):
    template_name = "payments/failure.html"


class PaymentPendingView(TemplateView):
    template_name = "payments/pending.html"


@method_decorator(csrf_exempt, name="dispatch")
class MercadoPagoWebhookView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            PaymentService().process_webhook(data)
        except Exception as e:
            logger.error(f"Webhook error: {e}")
        return HttpResponse(status=200)
