from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .services import DeliveryService

@receiver(post_save, sender=Order)
def trigger_delivery_assignment(sender, instance, created, **kwargs):
    """
    Automatically trigger delivery partner assignment when an order is confirmed.
    """
    if not created:
        # Check if the status has changed to CONFIRMED
        # and if an assignment doesn't already exist.
        if instance.status == Order.Status.CONFIRMED:
            if not hasattr(instance, 'delivery_assignment'):
                DeliveryService.assign_partner(instance)
