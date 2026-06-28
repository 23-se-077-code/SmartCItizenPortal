from django.core.management.base import BaseCommand
from datetime import date, timedelta
from challan.models import BillCategory, ChallanCategory, Bill, Challan

class Command(BaseCommand):
    help = 'Generate sample bills and challans for testing'

    def handle(self, *args, **kwargs):
        # Categories
        bill_cats = [
            {'name': 'Electricity', 'slug': 'electricity', 'icon': 'bi-bolt'},
            {'name': 'Sui Gas', 'slug': 'sui-gas', 'icon': 'bi-fire'},
            {'name': 'Water', 'slug': 'water', 'icon': 'bi-droplet'},
            {'name': 'Internet', 'slug': 'internet', 'icon': 'bi-wifi'},
        ]
        challan_cats = [
            {'name': 'Traffic Fine', 'slug': 'traffic-fine', 'icon': 'bi-car'},
            {'name': 'Court Challan', 'slug': 'court-challan', 'icon': 'bi-gavel'},
            {'name': 'Fee Challan', 'slug': 'fee-challan', 'icon': 'bi-file-earmark'},
        ]

        for cat in bill_cats:
            BillCategory.objects.get_or_create(slug=cat['slug'], defaults={'name': cat['name'], 'icon': cat['icon']})
        for cat in challan_cats:
            ChallanCategory.objects.get_or_create(slug=cat['slug'], defaults={'name': cat['name'], 'icon': cat['icon']})

        # Sample bills
        bill_category = BillCategory.objects.first()
        for i in range(1, 6):
            Bill.objects.get_or_create(
                consumer_number=f'CNS{i:04d}',
                defaults={
                    'consumer_name': f'Consumer {i}',
                    'category': bill_category,
                    'amount': 500 + i * 200,
                    'due_date': date.today() + timedelta(days=30),
                    'status': 'unpaid'
                }
            )

        # Sample challans
        challan_category = ChallanCategory.objects.first()
        for i in range(1, 6):
            Challan.objects.get_or_create(
                challan_number=f'CH{i:05d}',
                defaults={
                    'citizen_name': f'Citizen {i}',
                    'cnic': f'35201-123456{i}',
                    'category': challan_category,
                    'amount': 1000 + i * 500,
                    'due_date': date.today() + timedelta(days=15),
                    'status': 'unpaid',
                    'description': f'Challan issued for violation {i}'
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ Sample bills and challans created.'))