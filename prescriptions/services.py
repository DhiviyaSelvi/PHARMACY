from django.db import transaction
from .models import Prescription, PrescriptionAuditLog
from notifications.tasks import send_whatsapp_task

class PrescriptionService:
    @staticmethod
    @transaction.atomic
    def verify_prescription(prescription_id, pharmacist, status, notes=""):
        """
        Approves or Rejects a prescription.
        """
        if pharmacist.role != 'PHARMACIST':
            raise PermissionError("Only pharmacists can verify prescriptions.")

        prescription = Prescription.objects.get(id=prescription_id)
        old_status = prescription.status

        prescription.status = status
        prescription.pharmacist_notes = notes
        prescription.verified_by = pharmacist
        prescription.save()

        # Log the action
        PrescriptionAuditLog.objects.create(
            prescription=prescription,
            action=f"STATUS_CHANGE: {old_status} -> {status}",
            performed_by=pharmacist,
            notes=notes
        )

        # Notify User
        user = prescription.user
        if user.phone_number:
            msg = f"Your prescription verification is {status}. "
            if status == Prescription.Status.APPROVED:
                msg += "You can now proceed with your order for restricted medicines."
            else:
                msg += f"Reason: {notes}"
            send_whatsapp_task.delay(user.phone_number, msg)

        return prescription

    @staticmethod
    def link_to_order(prescription, order):
        # This can be used to ensure an order is backed by a valid prescription
        order.prescription_verified = True
        order.associated_prescription = prescription
        order.save()
