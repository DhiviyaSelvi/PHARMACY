from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DeliveryAssignment
from .serializers import DeliveryAssignmentSerializer
from .services import DeliveryService

class DeliveryPartnerViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only assignments for the logged-in partner
        return DeliveryAssignment.objects.filter(partner__user=self.request.user)

    @action(detail=True, methods=['post'])
    def pickup(self, request, pk=None):
        assignment = self.get_object()
        DeliveryService.pickup_order(assignment)
        return Response({'status': 'Picked Up'})

    @action(detail=True, methods=['post'])
    def start_delivery(self, request, pk=None):
        assignment = self.get_object()
        DeliveryService.start_out_for_delivery(assignment)
        return Response({'status': 'Out for Delivery - OTP Sent'})

    @action(detail=True, methods=['post'])
    def complete_delivery(self, request, pk=None):
        assignment = self.get_object()
        otp = request.data.get('otp')
        if DeliveryService.verify_and_complete(assignment, otp):
            return Response({'status': 'Delivered'})
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        assignment = self.get_object()
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')
        DeliveryService.update_live_location(assignment, lat, lon)
        return Response({'status': 'Location Updated'})
