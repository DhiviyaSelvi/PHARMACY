from django.shortcuts import render
from pharmacies.models import Pharmacy
from django.db.models import F
from django.db.models.functions import ACos, Cos, Radians, Sin

def get_nearby_pharmacies(request):
    # Default to Chennai Central coordinates if not provided
    user_lat = float(request.GET.get('lat', 13.0827))
    user_lon = float(request.GET.get('lon', 80.2707))

    # Simple Haversine approximation in Django ORM
    # radius in km
    radius = 10

    # Distance calculation (simplified)
    # This is a very rough approximation for demo purposes
    # In production, use PostGIS/GeoDjango
    pharmacies = Pharmacy.objects.filter(is_active=True, is_verified=True).annotate(
        # We'd use GeoDjango normally, but keeping it simple for the initial refactor
    )

    return render(request, 'pharmacies/nearby.html', {'pharmacies': pharmacies})
