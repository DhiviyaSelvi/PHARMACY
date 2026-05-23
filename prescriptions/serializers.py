from rest_framework import serializers
from .models import Prescription, PrescriptionAuditLog

class PrescriptionAuditLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True)

    class Meta:
        model = PrescriptionAuditLog
        fields = ['action', 'performed_by_name', 'notes', 'timestamp']

class PrescriptionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.username', read_only=True)
    audit_logs = PrescriptionAuditLogSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'user_name', 'image', 'status', 'pharmacist_notes',
            'verified_by_name', 'extracted_text', 'is_validated',
            'created_at', 'updated_at', 'audit_logs'
        ]
        read_only_fields = ['status', 'verified_by', 'extracted_text', 'is_validated', 'audit_logs']
