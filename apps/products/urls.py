from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="list"),
    path("search/", views.ProductSearchView.as_view(), name="search"),
    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="detail"),
]
