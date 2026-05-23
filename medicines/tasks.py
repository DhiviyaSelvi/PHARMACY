from celery import shared_task
from django.db import models
from .models import Inventory
from notifications.tasks import send_whatsapp_task

@shared_task
def check_low_stock_alerts():
    """
    Scans inventory for items below threshold and notifies pharmacists.
    """
    low_stock_items = Inventory.objects.filter(stock__lte=models.F('low_stock_threshold'), is_available=True).select_related('pharmacy', 'medicine')

    # Group by pharmacy to avoid spamming
    pharmacy_alerts = {}
    for item in low_stock_items:
        p_id = item.pharmacy.id
        if p_id not in pharmacy_alerts:
            pharmacy_alerts[p_id] = {'pharmacy': item.pharmacy, 'items': []}
        pharmacy_alerts[p_id]['items'].append(item.medicine.name)

    for p_id, data in pharmacy_alerts.items():
        pharmacy = data['pharmacy']
        items_str = ", ".join(data['items'])
        if pharmacy.contact_number:
            msg = f"Low Stock Alert for {pharmacy.name}! The following items need restock: {items_str}."
            send_whatsapp_task.delay(pharmacy.contact_number, msg)
