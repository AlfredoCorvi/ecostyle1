"""
Capa de Negocio - App: products
Vistas basadas en clases (CBV) - Regla #4
Toda logica de filtrado y busqueda aqui, nunca en los templates.
"""
from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg
from .models import Product, Category


class ProductListView(ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")
        # Filtros desde GET params
        category_slug = self.request.GET.get("category")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        sustainability = self.request.GET.get("sustainability")
        sort = self.request.GET.get("sort", "-created_at")

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if sustainability:
            qs = qs.filter(sustainability_level=sustainability)

        allowed_sorts = ["price", "-price", "-created_at", "name"]
        if sort in allowed_sorts:
            qs = qs.order_by(sort)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.filter(is_active=True)
        ctx["current_filters"] = self.request.GET
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related(
            "images", "reviews__user"
        ).select_related("category")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["avg_rating"] = self.object.reviews.aggregate(avg=Avg("rating"))["avg"]
        ctx["related_products"] = Product.objects.filter(
            category=self.object.category, is_active=True
        ).exclude(pk=self.object.pk)[:4]
        return ctx


class ProductSearchView(ListView):
    model = Product
    template_name = "products/search.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if not query:
            return Product.objects.none()
        # Busqueda con Q objects (Requerimiento #2)
        return Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(category__name__icontains=query),
            is_active=True
        ).distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class CategoryDetailView(ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs["slug"])
        return Product.objects.filter(category=self.category, is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current_category"] = self.category
        ctx["categories"] = Category.objects.filter(is_active=True)
        return ctx
