from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("checkout/<str:order_number>/", views.PaymentCheckoutView.as_view(), name="checkout"),
    path("success/", views.PaymentSuccessView.as_view(), name="success"),
    path("failure/", views.PaymentFailureView.as_view(), name="failure"),
    path("pending/", views.PaymentPendingView.as_view(), name="pending"),
    path("webhook/", views.MercadoPagoWebhookView.as_view(), name="webhook"),
]
