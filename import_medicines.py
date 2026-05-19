import csv
import os
import django
import sys

# Add the current directory to sys.path to ensure we can import settings correctly
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_project.settings')
django.setup()

from pharmacy.models import Category, Medicine

def import_medicines(file_path):
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
