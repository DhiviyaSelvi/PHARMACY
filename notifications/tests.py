from django.test import TestCase
from unittest.mock import patch, MagicMock
from .tasks import send_whatsapp_task, send_email_task, send_sms_task

class NotificationTaskTest(TestCase):
    @patch('notifications.services.NotificationService.send_whatsapp')
    def test_send_whatsapp_task(self, mock_send):
        mock_send.return_value = "MS123"
        send_whatsapp_task("+919876543210", "Test Message")
        mock_send.assert_called_once_with("+919876543210", "Test Message")

    @patch('notifications.services.NotificationService.send_sms')
    def test_send_sms_task(self, mock_send):
        mock_send.return_value = "MS456"
        send_sms_task("+919876543210", "Test SMS")
        mock_send.assert_called_once_with("+919876543210", "Test SMS")

    @patch('notifications.services.NotificationService.send_email')
    def test_send_email_task(self, mock_send):
        mock_send.return_value = 202
        send_email_task("test@example.com", "Subject", "<h1>Content</h1>")
        mock_send.assert_called_once_with("test@example.com", "Subject", "<h1>Content</h1>", None)
