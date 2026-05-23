from django.test import TestCase
from .models import Pharmacy
from .services import GeoLocationService
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class HyperlocalTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password')

        # Coimbatore Pharmacy (RS Puram area)
        self.pharm_cbe = Pharmacy.objects.create(
            owner=self.owner, name='Coimbatore Pharmacy', slug='cbe-pharm',
            latitude=Decimal('11.0011'), longitude=Decimal('76.9467'),
            district='Coimbatore', pincode='641002', is_verified=True
        )

        # Chennai Pharmacy
        self.pharm_chn = Pharmacy.objects.create(
            owner=self.owner, name='Chennai Pharmacy', slug='chn-pharm',
            latitude=Decimal('13.0827'), longitude=Decimal('80.2707'),
            district='Chennai', pincode='600001', is_verified=True
        )

    def test_haversine_accuracy(self):
        # Distance between RS Puram (11.0011, 76.9467) and Chennai Central (13.0827, 80.2707)
        # Approx 420-430 km
        dist = GeoLocationService.haversine(76.9467, 11.0011, 80.2707, 13.0827)
        self.assertTrue(420 < dist < 435)

    def test_nearby_logic(self):
        # User in Coimbatore
        nearby = GeoLocationService.get_nearby_pharmacies(11.0011, 76.9467, radius_km=20)
        self.assertEqual(len(nearby), 1)
        self.assertEqual(nearby[0].name, 'Coimbatore Pharmacy')

        # User in Chennai
        nearby_chn = GeoLocationService.get_nearby_pharmacies(13.0827, 80.2707, radius_km=20)
        self.assertEqual(len(nearby_chn), 1)
        self.assertEqual(nearby_chn[0].name, 'Chennai Pharmacy')
