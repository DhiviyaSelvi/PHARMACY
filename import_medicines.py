import csv
import os
import django
import sys

# Add the current directory to sys.path to ensure we can import settings correctly
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings')
django.setup()

from pharmacy.models import Category, Medicine, Pharmacy
from django.contrib.auth.models import User

def import_medicines(file_path):
    # Create a Default Pharmacy for initial data
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin_market', 'admin@market.com', 'admin123')

    default_pharmacy, _ = Pharmacy.objects.get_or_create(
        user=admin_user,
        defaults={
            'name': 'PharmaCare Central Warehouse',
            'license_number': 'LIC-CENTRAL-001',
            'address': 'PharmaCare HQ, Bangalore',
            'contact_email': 'warehouse@pharmacare.com',
            'contact_phone': '080-1234-5678',
            'is_verified': True
        }
    )

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    count = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                category_name = row['category'].strip()
                category, _ = Category.objects.get_or_create(name=category_name)

                medicine, created = Medicine.objects.update_or_create(
                    name=row['name'].strip(),
                    defaults={
                        'pharmacy': default_pharmacy,
                        'company': row['company'].strip(),
                        'category': category,
                        'price': row['price'],
                        'stock': row['stock'],
                        'image': row['image'].strip()
                    }
                )
                count += 1
            except Exception as e:
                print(f"Error importing row {row}: {e}")

    print(f"Import complete! {count} medicines processed.")

if __name__ == "__main__":
    import_medicines('medicines.csv')
