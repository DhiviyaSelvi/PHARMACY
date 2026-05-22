from django.contrib import admin
# Modular Imports
from pharmacies.models import Pharmacy
from medicines.models import Medicine, Category, Inventory
from orders.models import Order, OrderItem

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'is_verified')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'pharmacy', 'price', 'stock')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pharmacy', 'status', 'total_amount', 'created_at')
    inlines = [OrderItemInline]
