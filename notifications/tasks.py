from celery import shared_task
from .services import NotificationService

@shared_task(bind=True, max_retries=3)
def send_whatsapp_task(self, to_number, message_body):
    try:
        return NotificationService.send_whatsapp(to_number, message_body)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@shared_task(bind=True, max_retries=3)
def send_sms_task(self, to_number, message_body):
    try:
        return NotificationService.send_sms(to_number, message_body)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@shared_task(bind=True, max_retries=3)
def send_email_task(self, to_email, subject, html_content, attachment_data=None):
    try:
        return NotificationService.send_email(to_email, subject, html_content, attachment_data)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
