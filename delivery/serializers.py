from rest_framework import serializers
from .models import DeliveryAssignment, DeliveryTracking, DeliveryPartner

class DeliveryTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTracking
        fields = ['latitude', 'longitude', 'timestamp']

class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='order.user.username', read_only=True)
    pharmacy_name = serializers.CharField(source='order.pharmacy.name', read_only=True)
    delivery_address = serializers.CharField(source='order.delivery_address', read_only=True)
    latest_tracking = DeliveryTrackingSerializer(source='tracking_history.first', read_only=True)

    class Meta:
        model = DeliveryAssignment
        fields = [
            'id', 'status', 'assigned_at', 'picked_up_at', 'delivered_at',
            'customer_name', 'pharmacy_name', 'delivery_address', 'latest_tracking'
        ]
