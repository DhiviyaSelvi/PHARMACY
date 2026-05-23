from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Medicine, Category, Inventory
from .serializers import MedicineSerializer, CategorySerializer, InventorySerializer
from .services import SymptomSearchService

class MedicineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'requires_prescription']
    search_fields = ['name', 'brand', 'composition', 'description']
    ordering_fields = ['name', 'created_at']
    lookup_field = 'slug'

    @action(detail=False, methods=['get'])
    def symptom_search(self, request):
        query = request.query_params.get('q', '')
        results = SymptomSearchService.find_medicines(query)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def recommendations(self, request, slug=None):
        medicine = self.get_object()
        # Simple category-based recommendation logic for mobile
        recommendations = Medicine.objects.filter(
            category=medicine.category
        ).exclude(id=medicine.id)[:5]
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)

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
