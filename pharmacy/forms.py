from django import forms
from orders.models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address']
