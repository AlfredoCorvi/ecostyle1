"""
Capa de Negocio - App: cart
Las vistas solo orquestan; la logica va en CartService.
"""
import json
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import render
from .services import CartService


class CartDetailView(TemplateView):
    template_name = "cart/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cart"] = CartService.get_or_create_cart(self.request)
        return ctx


class AddToCartView(View):
    """Agrega producto via AJAX o POST normal."""
    def post(self, request):
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        try:
            cart = CartService.get_or_create_cart(request)
            item = CartService.add_item(cart, product_id, quantity)
            return JsonResponse({
                "success": True,
                "cart_total_items": cart.total_items,
                "message": f"{item.product.name} agregado al carrito.",
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)


class UpdateCartView(View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 0))
        try:
            cart = CartService.get_or_create_cart(request)
            CartService.update_quantity(cart, product_id, quantity)
            return JsonResponse({"success": True, "cart_total_items": cart.total_items})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)


class RemoveFromCartView(View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        cart = CartService.get_or_create_cart(request)
        CartService.remove_item(cart, product_id)
        return JsonResponse({"success": True, "cart_total_items": cart.total_items})
