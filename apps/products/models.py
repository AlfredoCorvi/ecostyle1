"""
Capa de Datos - App: products
Modelos: Category, Product, ProductImage, Review
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField("Descripcion", blank=True)
    image = models.ImageField("Imagen", upload_to="categories/", blank=True, null=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="children"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    class SustainabilityLevel(models.TextChoices):
        BASIC = "basic", "Basico"
        ECO = "eco", "Eco-Friendly"
        ORGANIC = "organic", "Organico"
        ZERO_WASTE = "zero_waste", "Zero Waste"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField("Nombre", max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=300)
    description = models.TextField("Descripcion")
    short_description = models.CharField("Descripcion corta", max_length=300, blank=True)
    price = models.DecimalField("Precio", max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    compare_price = models.DecimalField("Precio comparativo", max_digits=10,
                                        decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField("Stock", default=0)
    sku = models.CharField("SKU", max_length=100, unique=True, blank=True)
    sustainability_level = models.CharField(
        "Nivel de sostenibilidad", max_length=20,
        choices=SustainabilityLevel.choices, default=SustainabilityLevel.ECO
    )
    materials = models.TextField("Materiales", blank=True)
    is_active = models.BooleanField("Activo", default=True)
    is_featured = models.BooleanField("Destacado", default=False)
    weight = models.DecimalField("Peso (kg)", max_digits=6, decimal_places=3,
                                  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name="price_non_negative"),
            models.CheckConstraint(check=models.Q(stock__gte=0), name="stock_non_negative"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"ECO-{self.category.id}-{slugify(self.name)[:20].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def main_image(self):
        img = self.images.filter(is_primary=True).first()
        return img or self.images.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("Imagen", upload_to="products/")
    alt_text = models.CharField("Texto alternativo", max_length=200, blank=True)
    is_primary = models.BooleanField("Imagen principal", default=False)
    order = models.PositiveSmallIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Imagen de Producto"
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        # Solo una imagen puede ser principal por producto
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Imagen de {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        "Calificacion", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField("Titulo", max_length=200)
    body = models.TextField("Comentario")
    is_verified_purchase = models.BooleanField("Compra verificada", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resena"
        verbose_name_plural = "Resenas"
        unique_together = [("product", "user")]  # Un usuario, una resena por producto
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="review_rating_range"
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}/5)"
    
   
class Brand(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField("Activo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField("Nombre", max_length=50, unique=True)

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="variants"
    )
    name = models.CharField("Nombre variante", max_length=100)  # Ej: "Rojo - M"
    price = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField("Stock", default=0)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Variante de Producto"
        verbose_name_plural = "Variantes de Producto"
        ordering = ["product", "name"]
        

    def __str__(self):
        return f"{self.product.name} - {self.name}"