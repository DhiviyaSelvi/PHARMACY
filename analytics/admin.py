from django.contrib import admin
from orders.models import Order, OrderItem, Cart, CartItem
from payments.models import Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('transaction_id', 'provider_order_id', 'provider_payment_id')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pharmacy', 'status', 'total_amount', 'prescription_verified', 'created_at')
    list_filter = ('status', 'prescription_verified', 'created_at', 'pharmacy__city')
    search_fields = ('user__username', 'id', 'transaction_id')
    inlines = [OrderItemInline, PaymentInline]

    actions = ['cancel_orders', 'confirm_orders']

    def confirm_orders(self, request, queryset):
        queryset.update(status=Order.Status.CONFIRMED)
    confirm_orders.short_description = "Confirm selected orders"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'status', 'amount', 'transaction_id', 'created_at')
    list_filter = ('status', 'method')
    search_fields = ('transaction_id', 'provider_payment_id')
