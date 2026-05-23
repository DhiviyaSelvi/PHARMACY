from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Prescription, PrescriptionAuditLog
from .services import PrescriptionService

class AuditLogInline(admin.TabularInline):
    model = PrescriptionAuditLog
    extra = 0
    readonly_fields = ('action', 'performed_by', 'notes', 'timestamp')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'verified_by', 'created_at', 'view_image_link')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'pharmacist_notes')
    readonly_fields = ('verified_by', 'is_validated', 'extracted_text')
    inlines = [AuditLogInline]

    actions = ['approve_prescriptions', 'reject_prescriptions']

    def view_image_link(self, obj):
        if obj.image:
            return format_html('<a href="{}" target="_blank">View Prescription</a>', obj.image.url)
        return "No Image"
    view_image_link.short_description = "Image"

    def approve_prescriptions(self, request, queryset):
        for obj in queryset:
            PrescriptionService.verify_prescription(obj.id, request.user, Prescription.Status.APPROVED, "Approved via bulk action")
        self.message_user(request, f"Approved {queryset.count()} prescriptions.")
    approve_prescriptions.short_description = "Approve selected prescriptions"

    def reject_prescriptions(self, request, queryset):
        for obj in queryset:
            PrescriptionService.verify_prescription(obj.id, request.user, Prescription.Status.REJECTED, "Rejected via bulk action")
        self.message_user(request, f"Rejected {queryset.count()} prescriptions.")
    reject_prescriptions.short_description = "Reject selected prescriptions"
