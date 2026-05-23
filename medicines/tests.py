from django.test import TestCase
from .models import Medicine, Category, Inventory
from .services import SymptomSearchService

class AIFeatureTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Fever", slug="fever")
        self.med = Medicine.objects.create(
            name="Paracetamol", slug="paracetamol", brand="GSK",
            category=self.cat, description="Used for fever and pain"
        )

    def test_symptom_search(self):
        results = SymptomSearchService.find_medicines("fever")
        self.assertIn(self.med, results)

        # Tamil support
        results_ta = SymptomSearchService.find_medicines("காய்ச்சல்")
        self.assertIn(self.med, results_ta)
