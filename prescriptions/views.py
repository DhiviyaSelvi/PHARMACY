from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Prescription
from .services import PrescriptionService, OCRService

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'PHARMACIST':
            return Prescription.objects.filter(status='PENDING')
        return Prescription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        prescription = serializer.save(user=self.request.user)
        # Trigger OCR analysis automatically on upload
        if prescription.image:
            text = OCRService.extract_text(prescription.image.path)
            prescription.extracted_text = text
            prescription.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def verify(self, request, pk=None):
        prescription = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')

        try:
            PrescriptionService.verify_prescription(prescription.id, request.user, new_status, notes)
            return Response({'status': 'updated'})
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
