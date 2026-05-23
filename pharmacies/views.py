from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pharmacy
from .serializers import PharmacySerializer
from .services import GeoLocationService

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

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        radius = request.query_params.get('radius', 10)

        if not lat or not lon:
            return Response({"error": "lat and lon are required"}, status=400)

        nearby_pharmacies = GeoLocationService.get_nearby_pharmacies(lat, lon, float(radius))
        serializer = self.get_serializer(nearby_pharmacies, many=True)

        # Attach distances to serialized data
        data = serializer.data
        for i, obj in enumerate(nearby_pharmacies):
            data[i]['distance_km'] = obj.distance

        return Response(data)

    @action(detail=False, methods=['get'])
    def region(self, request):
        pincode = request.query_params.get('pincode')
        district = request.query_params.get('district')

        pharmacies = GeoLocationService.filter_by_region(pincode, district)
        serializer = self.get_serializer(pharmacies, many=True)
        return Response(serializer.data)
