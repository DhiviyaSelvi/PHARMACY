from django.db import models
from pharmacies.models import Pharmacy

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Medicine(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='medicines')
    description = models.TextField()
    composition = models.TextField(help_text="Chemical composition")
    side_effects = models.TextField(blank=True)
    usage_instructions = models.TextField(blank=True)

    requires_prescription = models.BooleanField(default=False)

    image = models.ImageField(upload_to='medicine_images/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='inventory')
    warehouse = models.ForeignKey('pharmacies.Warehouse', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='pharmacy_stock')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)

    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('pharmacy', 'medicine')
        verbose_name_plural = "Inventory"

    def __str__(self):
        return f"{self.medicine.name} at {self.pharmacy.name}"
