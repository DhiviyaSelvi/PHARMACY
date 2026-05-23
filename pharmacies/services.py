from math import radians, cos, sin, asin, sqrt
from .models import Pharmacy

class GeoLocationService:
    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c * r

    @classmethod
    def get_nearby_pharmacies(cls, user_lat, user_lon, radius_km=10):
        """
        Returns a list of verified pharmacies within the given radius,
        sorted by proximity.
        """
        pharmacies = Pharmacy.objects.filter(is_verified=True, is_active=True)
        nearby = []

        for pharm in pharmacies:
            if pharm.latitude and pharm.longitude:
                dist = cls.haversine(user_lon, user_lat, pharm.longitude, pharm.latitude)
                if dist <= radius_km:
                    pharm.distance = round(dist, 2)
                    nearby.append(pharm)

        return sorted(nearby, key=lambda x: x.distance)

    @staticmethod
    def filter_by_region(pincode=None, district=None):
        """
        Filters pharmacies by exact pincode or district.
        """
        queryset = Pharmacy.objects.filter(is_verified=True, is_active=True)
        if pincode:
            queryset = queryset.filter(pincode=pincode)
        if district:
            queryset = queryset.filter(district__iexact=district)
        return queryset
