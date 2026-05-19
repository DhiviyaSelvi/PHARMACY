import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings')
django.setup()

from pharmacy.models import Category, Medicine

def import_medicines(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category, _ = Category.objects.get_or_create(name=row['category'])
            Medicine.objects.get_or_create(
                name=row['name'],
                company=row['company'],
                category=category,
                price=row['price'],
                stock=row['stock'],
                image=row['image']
            )
    print("Import complete!")

if __name__ == "__main__":
    import_medicines('medicines.csv')
