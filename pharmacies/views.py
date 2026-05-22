from rest_framework import viewsets, permissions
from .models import Pharmacy
from .serializers import PharmacySerializer

class PharmacyViewSet(viewsets.ModelViewSet):
    queryset = Pharmacy.objects.filter(is_active=True, is_verified=True)
    serializer_class = PharmacySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
