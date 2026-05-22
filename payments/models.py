from django.db import models
from orders.models import Order

class Payment(models.Model):
    class Method(models.TextChoices):
        RAZORPAY = "RAZORPAY", "Razorpay"
        UPI_MANUAL = "UPI", "Manual UPI"
        CASH = "CASH", "Cash on Delivery"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    # Provider specific
    provider_order_id = models.CharField(max_length=100, null=True, blank=True)
    provider_payment_id = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
