"""
Capa de Datos - App: accounts
Extiende el User de Django con un perfil adicional (patron 1:1).
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField("Telefono", max_length=20, blank=True)
    avatar = models.ImageField("Avatar", upload_to="avatars/", blank=True, null=True)
    address_line1 = models.CharField("Direccion", max_length=255, blank=True)
    address_line2 = models.CharField("Colonia", max_length=255, blank=True)
    city = models.CharField("Ciudad", max_length=100, blank=True)
    state = models.CharField("Estado", max_length=100, blank=True)
    postal_code = models.CharField("Codigo Postal", max_length=10, blank=True)
    country = models.CharField("Pais", max_length=100, default="Mexico")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.email}"

    @property
    def full_address(self):
        parts = filter(None, [self.address_line1, self.address_line2,
                               self.city, self.state, self.postal_code, self.country])
        return ", ".join(parts)


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
