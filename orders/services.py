from django.db import transaction
from .models import Order, OrderItem
from medicines.models import Inventory
from notifications.tasks import send_whatsapp_task, send_email_task
from .invoices import InvoiceService

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, cart_data, shipping_details):
        """
        cart_data: list of dicts {'inventory_id': id, 'quantity': q}
        shipping_details: dict with full_name, phone, delivery_address, city, pincode
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
                full_name=shipping_details.get('full_name', ''),
                phone=shipping_details.get('phone', ''),
                delivery_address=shipping_details.get('delivery_address', ''),
                city=shipping_details.get('city', ''),
                pincode=shipping_details.get('pincode', ''),
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

            # Send Notification: Order Placed
            if user.phone_number:
                msg = f"வணக்கம் {user.username}! Your order {order.id} for {order.total_amount} at {pharmacy.name} has been placed."
                send_whatsapp_task.delay(user.phone_number, msg)

            if user.email:
                subject = f"Order Placed: #{order.id}"
                content = f"<h1>Order Confirmed</h1><p>Your order at {pharmacy.name} is being processed.</p>"

                # Generate Invoice and Attach
                invoice_b64 = InvoiceService.generate_order_invoice_base64(order)
                attachment = {
                    'content': invoice_b64,
                    'filename': f'invoice_{order.id}.pdf',
                    'file_type': 'application/pdf'
                }
                send_email_task.delay(user.email, subject, content, attachment)

        return orders
