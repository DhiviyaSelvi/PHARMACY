from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Medicine, Category, Inventory
from .serializers import MedicineSerializer, CategorySerializer, InventorySerializer

class MedicineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'requires_prescription']
    search_fields = ['name', 'brand', 'composition', 'description']
    ordering_fields = ['name', 'created_at']
    lookup_field = 'slug'

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.filter(is_available=True, stock__gt=0)
    serializer_class = InventorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['pharmacy', 'medicine', 'pharmacy__city']
    ordering_fields = ['price', 'stock']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
