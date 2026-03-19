from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("<str:order_number>/confirmation/", views.OrderConfirmationView.as_view(), name="confirmation"),
    path("history/", views.OrderHistoryView.as_view(), name="history"),
]
