from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Medicine(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)

    company = models.CharField(max_length=200)

    price = models.IntegerField()

    stock = models.IntegerField(default=0)

    image = models.URLField(blank=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Cart(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)

    def subtotal(self):

        return self.quantity * self.medicine.price

    def __str__(self):
        return self.medicine.name


class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=20)

    address = models.TextField()

    city = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.medicine.name