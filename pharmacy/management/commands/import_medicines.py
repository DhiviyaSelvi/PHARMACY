import csv

from django.core.management.base import BaseCommand

from pharmacy.models import Medicine, Category


class Command(BaseCommand):

    help = 'Import medicines from CSV'

    def handle(self, *args, **kwargs):

        with open('medicines.csv', newline='', encoding='utf-8') as file:

            reader = csv.DictReader(file)

            for row in reader:

                category, created = Category.objects.get_or_create(
                    name=row['category']
                )

                Medicine.objects.create(
                    name=row['name'],
                    company=row['company'],
                    category=category,
                    price=row['price'],
                    stock=row['stock'],
                    image=row['image']
                )

        self.stdout.write(
            self.style.SUCCESS('Medicines imported successfully!')
        )