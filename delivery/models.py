from django.db import models
from django.conf import settings
from orders.models import Order
import random
import string

class Zone(models.Model):
    name = models.CharField(max_length=100) # e.g., "Chennai-Central", "Coimbatore-North"
    city = models.CharField(max_length=100)
    pincodes = models.TextField(help_text="Comma-separated pincodes in this zone")

    def __str__(self):
        return f"{self.city} - {self.name}"

class DeliveryPartner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_profile')
    is_available = models.BooleanField(default=True)
    current_zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_number = models.CharField(max_length=20)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)

    def __str__(self):
        return f"Partner: {self.user.username}"

class DeliveryAssignment(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        PICKED_UP = "PICKED_UP", "Picked Up"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_assignment')
    partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, related_name='assignments')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ASSIGNED)

    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id}"

class DeliveryTracking(models.Model):
    assignment = models.ForeignKey(DeliveryAssignment, on_delete=models.CASCADE, related_name='tracking_history')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class DeliveryOTP(models.Model):
    assignment = models.OneToOneField(DeliveryAssignment, on_delete=models.CASCADE, related_name='otp_verification')
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        self.otp_code = ''.join(random.choices(string.digits, k=6))
        self.save()
        return self.otp_code
