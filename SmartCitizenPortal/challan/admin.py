from django.contrib import admin
from .models import BillCategory, ChallanCategory, Bill, Challan, PaymentTransaction

admin.site.register(BillCategory)
admin.site.register(ChallanCategory)
admin.site.register(Bill)
admin.site.register(Challan)
admin.site.register(PaymentTransaction)