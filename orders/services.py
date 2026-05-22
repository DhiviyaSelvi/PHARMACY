from django.db import transaction
from .models import Order, OrderItem
from medicines.models import Inventory

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, cart_data, delivery_address):
        """
        cart_data: list of dicts {'inventory_id': id, 'quantity': q}
        This logic handles splitting orders by pharmacy.
        """
        orders = []
        # Group items by pharmacy
        pharmacy_items = {}
        for item in cart_data:
            inventory = Inventory.objects.select_related('pharmacy').get(id=item['inventory_id'])
            pharm_id = inventory.pharmacy.id
            if pharm_id not in pharmacy_items:
                pharmacy_items[pharm_id] = []
            pharmacy_items[pharm_id].append({
                'inventory': inventory,
                'quantity': item['quantity']
            })

        for pharm_id, items in pharmacy_items.items():
            pharmacy = items[0]['inventory'].pharmacy
            total_amount = sum(i['inventory'].price * i['quantity'] for i in items)

            order = Order.objects.create(
                user=user,
                pharmacy=pharmacy,
                total_amount=total_amount,
                delivery_address=delivery_address,
                status=Order.Status.PENDING
            )

            for i in items:
                OrderItem.objects.create(
                    order=order,
                    inventory_item=i['inventory'],
                    quantity=i['quantity'],
                    price_at_order=i['inventory'].price
                )
                # Atomic stock reduction
                i['inventory'].stock -= i['quantity']
                i['inventory'].save()

            orders.append(order)

        return orders
