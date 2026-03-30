from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("create/<int:order_id>/", views.CreatePaymentView.as_view(), name="create"),
    path("success/",               views.PaymentSuccessView.as_view(),  name="success"),
    path("failure/",               views.PaymentFailureView.as_view(),  name="failure"),
    path("pending/",               views.PaymentPendingView.as_view(),  name="pending"),
    path("webhook/",               views.PaymentWebhookView.as_view(),  name="webhook"),
    path("checkout/<str:order_number>/", views.PaymentCheckoutView.as_view(), name="checkout"),
]