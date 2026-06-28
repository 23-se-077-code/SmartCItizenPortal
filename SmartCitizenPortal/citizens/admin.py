from django.contrib import admin
from .models import Citizen, Household, Address, FamilyMember, Document, Application

@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'cnic', 'status', 'created_at')
    list_filter = ('status', 'gender', 'marital_status')
    search_fields = ('full_name', 'cnic', 'phone', 'email')

admin.site.register(Household)
admin.site.register(Address)
admin.site.register(FamilyMember)
admin.site.register(Document)
admin.site.register(Application)