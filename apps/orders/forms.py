from django import forms


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="Nombre")
    last_name = forms.CharField(max_length=50, label="Apellido")
    phone = forms.CharField(max_length=20, label="Teléfono")
    address_line1 = forms.CharField(max_length=255, label="Dirección")
    address_line2 = forms.CharField(max_length=255, label="Colonia/Apto", required=False)
    city = forms.CharField(max_length=100, label="Ciudad")
    state = forms.CharField(max_length=100, label="Estado")
    postal_code = forms.CharField(max_length=10, label="Código Postal")
    country = forms.CharField(max_length=100, initial="México", label="País")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and hasattr(user, "profile"):
            p = user.profile
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["phone"].initial = p.phone
            self.fields["address_line1"].initial = p.address_line1
            self.fields["city"].initial = p.city
            self.fields["state"].initial = p.state
            self.fields["postal_code"].initial = p.postal_code
