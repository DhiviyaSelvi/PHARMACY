import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from medicines.models import Medicine, Category, Inventory
from pharmacies.models import Pharmacy

User = get_user_model()

def import_data():
    # 1. Create a Pharmacist User
    owner, created = User.objects.get_or_create(
        username='admin_pharmacy',
        defaults={'role': User.Role.PHARMACIST}
    )
    if created:
        owner.set_password('admin123')
        owner.save()

    # 2. Create a Pharmacy
    pharmacy, _ = Pharmacy.objects.get_or_create(
        owner=owner,
        name='Apollo Pharmacy - Chennai',
        slug='apollo-chennai',
        defaults={
            'license_number': 'TN-12345',
            'address': 'Anna Salai, Chennai',
            'district': 'Chennai',
            'contact_number': '9876543210',
            'is_verified': True
        }
    )

    # 3. Create Categories
    fever, _ = Category.objects.get_or_create(name='Fever', slug='fever')
    antibiotics, _ = Category.objects.get_or_create(name='Antibiotics', slug='antibiotics')

    # 4. Create Medicines and Inventory
    medicines_data = [
        {'name': 'Paracetamol 500mg', 'brand': 'GSK', 'price': 15.50, 'category': fever},
        {'name': 'Amoxicillin 250mg', 'brand': 'Cipla', 'price': 45.00, 'category': antibiotics},
    ]

    for data in medicines_data:
        medicine, _ = Medicine.objects.get_or_create(
            name=data['name'],
            slug=data['name'].lower().replace(' ', '-'),
            defaults={
                'brand': data['brand'],
                'category': data['category'],
                'description': f"High quality {data['name']}"
            }
        )

        Inventory.objects.get_or_create(
            pharmacy=pharmacy,
            medicine=medicine,
            defaults={
                'price': data['price'],
                'stock': 100,
                'is_available': True
            }
        )

    print("Data imported successfully to modular models.")

if __name__ == "__main__":
    import_data()
