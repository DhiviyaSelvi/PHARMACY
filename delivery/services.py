from django.utils import timezone
from .models import DeliveryAssignment, DeliveryPartner, DeliveryOTP, DeliveryTracking
from notifications.tasks import send_whatsapp_task

class DeliveryService:
    @staticmethod
    def assign_partner(order):
        """
        Logic to find the best available partner in the order's zone.
        """
        # Simplified: Assign any available partner for now
        partner = DeliveryPartner.objects.filter(is_available=True).first()
        if partner:
            assignment = DeliveryAssignment.objects.create(
                order=order,
                partner=partner,
                status=DeliveryAssignment.Status.ASSIGNED
            )
            partner.is_available = False
            partner.save()

            # Notify Partner
            msg = f"New Delivery Assigned! Order #{order.id} at {order.pharmacy.name}."
            if partner.user.phone_number:
                send_whatsapp_task.delay(partner.user.phone_number, msg)
            return assignment
        return None

    @staticmethod
    def pickup_order(assignment):
        assignment.status = DeliveryAssignment.Status.PICKED_UP
        assignment.picked_up_at = timezone.now()
        assignment.save()

        # Notify Customer
        user = assignment.order.user
        if user.phone_number:
            send_whatsapp_task.delay(user.phone_number, f"உங்கள் மருந்து பார்சல் டெலிவரிக்காக எடுக்கப்பட்டது! Order #{assignment.order.id} is picked up.")

    @staticmethod
    def start_out_for_delivery(assignment):
        assignment.status = DeliveryAssignment.Status.OUT_FOR_DELIVERY
        assignment.save()

        # Generate and Send OTP
        otp_obj, _ = DeliveryOTP.objects.get_or_create(assignment=assignment)
        otp_code = otp_obj.generate_otp()

        user = assignment.order.user
        if user.phone_number:
            msg = f"உங்கள் ஆர்டர் டெலிவரிக்கு வந்துவிட்டது! OTP: {otp_code}. Share this with the delivery partner."
            send_whatsapp_task.delay(user.phone_number, msg)

    @staticmethod
    def verify_and_complete(assignment, entered_otp):
        otp_obj = assignment.otp_verification
        if otp_obj.otp_code == entered_otp:
            otp_obj.is_verified = True
            otp_obj.save()

            assignment.status = DeliveryAssignment.Status.DELIVERED
            assignment.delivered_at = timezone.now()
            assignment.save()

            # Complete Order
            assignment.order.status = assignment.order.Status.DELIVERED
            assignment.order.save()

            # Make partner available again
            assignment.partner.is_available = True
            assignment.partner.save()
            return True
        return False

    @staticmethod
    def update_live_location(assignment, lat, lon):
        DeliveryTracking.objects.create(
            assignment=assignment,
            latitude=lat,
            longitude=lon
        )
