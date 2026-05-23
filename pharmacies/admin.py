from django.contrib import admin
from django.utils.html import format_html
from .models import Pharmacy

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'district', 'is_verified', 'is_active', 'rating', 'verify_pharmacy_btn')
    list_filter = ('is_verified', 'is_active', 'district', 'city')
    search_fields = ('name', 'license_number', 'address')

    actions = ['mark_verified', 'mark_unverified']

    def verify_pharmacy_btn(self, obj):
        if not obj.is_verified:
            return format_html('<span style="color: red;">Pending Approval</span>')
        return format_html('<span style="color: green;">Verified</span>')
    verify_pharmacy_btn.short_description = "Status"

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_verified.short_description = "Verify selected pharmacies"
