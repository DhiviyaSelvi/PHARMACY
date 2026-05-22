from django.db import models
from django.conf import settings

class Pharmacy(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_pharmacies'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    license_number = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100, default="Chennai")
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=15)

    # Location for hyperlocal delivery
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Pharmacies"
