"""
Capa de Negocio - App: cart
Las vistas solo orquestan; la logica va en CartService.
"""
import json
from django.forms import ValidationError
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import render
from .services import CartService


class CartDetailView(TemplateView):
    template_name = "cart/detail.html"

    def get_context_data(self, **kwargs):
        ctx    = super().get_context_data(**kwargs)
        cart   = CartService.get_or_create_cart(self.request)

        # ── DEBUG TEMPORAL ────────────────────────────
        print(f"DEBUG → User: {self.request.user}")
        print(f"DEBUG → Cart ID: {cart.id}")
        print(f"DEBUG → Items: {cart.items.count()}")
        print(f"DEBUG → is_empty: {cart.is_empty}")
        # ─────────────────────────────────────────────

        totals = CartService.get_totals(cart)
        ctx['cart']                    = cart
        ctx['items']                   = cart.items.select_related('product__category').all()
        ctx['subtotal']                = totals['subtotal']
        ctx['tax']                     = totals['tax']
        ctx['shipping']                = totals['shipping']
        ctx['total']                   = totals['total']
        ctx['free_shipping']           = totals['free_shipping']
        ctx['free_shipping_remaining'] = totals['free_shipping_remaining']
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
        raw_qty    = request.POST.get("quantity", "0")

        try:
            quantity = int(raw_qty)
        except (ValueError, TypeError):
            return JsonResponse(
                {"success": False, "message": f"Cantidad inválida: '{raw_qty}'"},
                status=400
            )

        if quantity < 0:
            return JsonResponse(
                {"success": False, "message": "La cantidad no puede ser negativa."},
                status=400
            )

        try:
            cart    = CartService.get_or_create_cart(request)
            item    = CartService.update_quantity(cart, product_id, quantity)
            totals  = CartService.get_totals(cart)

            return JsonResponse({
                "success":          True,
                "quantity":         quantity,
                "line_total":       f"{CartService.get_line_total(item):.2f}" if item else "0.00",
                "subtotal":         f"{totals['subtotal']:.2f}",
                "tax":              f"{totals['tax']:.2f}",
                "shipping":         f"{totals['shipping']:.2f}",
                "total":            f"{totals['total']:.2f}",
                "cart_total_items": cart.total_items,
            })
        except ValidationError as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)


class RemoveFromCartView(View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        cart = CartService.get_or_create_cart(request)
        CartService.remove_item(cart, product_id)
        return JsonResponse({
            "success": True,
            "cart_total_items": cart.total_items
        })
