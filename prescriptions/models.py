from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Prescription(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending Verification")
        APPROVED = "APPROVED", _("Approved")
        REJECTED = "REJECTED", _("Rejected")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    image = models.ImageField(upload_to='prescriptions/')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    pharmacist_notes = models.TextField(blank=True)

    # Metadata
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'PHARMACIST'},
        related_name='verified_prescriptions'
    )

    # OCR and content
    extracted_text = models.TextField(blank=True)
    is_validated = models.BooleanField(default=False) # AI/OCR validation flag

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prescription #{self.id} - {self.user.username} ({self.get_status_display()})"

class PrescriptionAuditLog(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
