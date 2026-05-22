import razorpay
from django.conf import settings
from .models import Payment

class RazorpayService:
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

    @classmethod
    def create_razorpay_order(cls, order_obj):
        amount_paise = int(order_obj.total_amount * 100)
        data = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"order_{order_obj.id}"
        }
        rp_order = cls.client.order.create(data=data)

        # Create/Update Payment record
        payment, _ = Payment.objects.update_or_create(
            order=order_obj,
            defaults={
                'method': Payment.Method.RAZORPAY,
                'amount': order_obj.total_amount,
                'provider_order_id': rp_order['id'],
                'status': Payment.Status.PENDING
            }
        )
        return rp_order

    @classmethod
    def verify_payment(cls, rp_order_id, rp_payment_id, rp_signature):
        params_dict = {
            'razorpay_order_id': rp_order_id,
            'razorpay_payment_id': rp_payment_id,
            'razorpay_signature': rp_signature
        }
        try:
            cls.client.utility.verify_payment_signature(params_dict)
            payment = Payment.objects.get(provider_order_id=rp_order_id)
            payment.status = Payment.Status.COMPLETED
            payment.provider_payment_id = rp_payment_id
            payment.save()

            # Update order status
            payment.order.status = payment.order.Status.CONFIRMED
            payment.order.save()
            return True
        except Exception:
            return False
