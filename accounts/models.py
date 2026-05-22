from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        PHARMACIST = "PHARMACIST", _("Pharmacist")
        BUYER = "BUYER", _("Buyer")
        DELIVERY_PARTNER = "DELIVERY", _("Delivery Partner")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.BUYER
    )
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, default="Chennai")
    pincode = models.CharField(max_length=10, blank=True)

    # Tamil Nadu specific fields
    district = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
