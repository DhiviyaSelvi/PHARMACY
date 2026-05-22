from rest_framework import serializers
from .models import Medicine, Category, Inventory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MedicineSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Medicine
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    medicine_details = MedicineSerializer(source='medicine', read_only=True)
    pharmacy_name = serializers.CharField(source='pharmacy.name', read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'
