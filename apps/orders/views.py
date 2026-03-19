from django.views.generic import FormView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem
from .forms import CheckoutForm
from apps.cart.services import CartService
from apps.payments.services import PaymentService


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = "orders/checkout.html"
    form_class = CheckoutForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cart"] = CartService.get_or_create_cart(self.request)
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        cart = CartService.get_or_create_cart(self.request)
        if cart.is_empty:
            messages.error(self.request, "Tu carrito está vacío.")
            return redirect("cart:detail")

        data = form.cleaned_data
        order = Order.objects.create(
            user=self.request.user,
            shipping_name=f"{data['first_name']} {data['last_name']}",
            shipping_email=self.request.user.email,
            shipping_phone=data["phone"],
            shipping_address=data["address_line1"],
            shipping_city=data["city"],
            shipping_state=data["state"],
            shipping_postal_code=data["postal_code"],
            shipping_country=data.get("country", "México"),
            subtotal=cart.subtotal,
            total=cart.subtotal,
        )

        for item in cart.items.select_related("product").all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_sku=item.product.sku,
                unit_price=item.product.price,
                quantity=item.quantity,
                subtotal=item.subtotal,
            )

        CartService.clear_cart(cart)
        return redirect("payments:checkout", order_number=order.order_number)


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/confirmation.html"
    context_object_name = "order"

    def get_object(self):
        return Order.objects.get(
            order_number=self.kwargs["order_number"],
            user=self.request.user
        )


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/history.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")
