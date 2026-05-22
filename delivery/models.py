from django.db import models
from orders.models import Order
from django.conf import settings

class Delivery(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        PICKED_UP = "PICKED_UP", "Picked Up"
        DELIVERED = "DELIVERED", "Delivered"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_details')
    delivery_partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'DELIVERY'}
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ASSIGNED)

    assigned_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Live tracking
    current_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None
        if not is_new:
            old_status = Delivery.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        # Trigger Notifications on Status Change
        from notifications.tasks import send_whatsapp_task
        if not is_new and self.status != old_status:
            user = self.order.user
            if user.phone_number:
                if self.status == Delivery.Status.PICKED_UP:
                    send_whatsapp_task.delay(user.phone_number, f"Order #{self.order.id} has been picked up and is out for delivery!")
                elif self.status == Delivery.Status.DELIVERED:
                    send_whatsapp_task.delay(user.phone_number, f"Order #{self.order.id} has been successfully delivered. Enjoy your health!")
