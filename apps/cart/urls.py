from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="detail"),
    path("add/", views.AddToCartView.as_view(), name="add"),
    path("update/", views.UpdateCartView.as_view(), name="update"),
    path("remove/", views.RemoveFromCartView.as_view(), name="remove"),
]
