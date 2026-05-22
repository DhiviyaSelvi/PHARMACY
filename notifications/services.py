import logging
from django.conf import settings
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

logger = logging.getLogger('notifications')

class NotificationService:
    @staticmethod
    def send_whatsapp(to_number, message_body):
        """
        Sends a WhatsApp message using Twilio.
        to_number: User's phone number (e.g. +91XXXXXXXXXX)
        """
        try:
            client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                body=message_body,
                to=f'whatsapp:{to_number}'
            )
            logger.info(f"WhatsApp sent to {to_number}: SID {message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {to_number}: {str(e)}")
            raise e

    @staticmethod
    def send_sms(to_number, message_body):
        """
        Sends a standard SMS using Twilio.
        """
        try:
            client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                from_=settings.TWILIO_PHONE_NUMBER,
                body=message_body,
                to=to_number
            )
            logger.info(f"SMS sent to {to_number}: SID {message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            raise e

    @staticmethod
    def send_email(to_email, subject, html_content, attachment_data=None):
        """
        Sends an email using SendGrid.
        attachment_data: dict with {'content': base64_str, 'filename': str, 'file_type': str}
        """
        try:
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )

            if attachment_data:
                encoded_file = attachment_data['content']
                attached_file = Attachment(
                    FileContent(encoded_file),
                    FileName(attachment_data['filename']),
                    FileType(attachment_data['file_type']),
                    Disposition('attachment')
                )
                message.add_attachment(attached_file)

            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            logger.info(f"Email sent to {to_email}: Status {response.status_code}")
            return response.status_code
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise e
