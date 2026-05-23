from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, Avg
from orders.models import Order
from delivery.models import DeliveryAssignment

class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        stats = {
            "total_sales": Order.objects.filter(status='DELIVERED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            "order_count": Order.objects.count(),
            "pending_prescriptions": Order.objects.filter(prescription_verified=False).count(),
            "delivery_performance": DeliveryAssignment.objects.filter(status='DELIVERED').aggregate(
                avg_delivery_time=Avg('delivered_at' - 'assigned_at')
            ),
            "city_distribution": Order.objects.values('pharmacy__city').annotate(count=Count('id'))
        }
        return Response(stats)
