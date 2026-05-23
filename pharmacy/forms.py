from django import forms
from orders.models import Order

class CheckoutForm(forms.ModelForm):
    PAYMENT_METHODS = [
        ('CASH', 'Cash on Delivery'),
        ('GPAY', 'Google Pay'),
        ('PHONEPE', 'PhonePe'),
        ('CARD', 'Credit/Debit Card'),
        ('RAZORPAY', 'Razorpay'),
    ]
    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, widget=forms.Select(attrs={'class': 'form-control'}))
    prescription = forms.ImageField(required=False)

    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'delivery_address', 'city', 'pincode', 'transaction_id', 'prescription']
