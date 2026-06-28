from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'reference_number', 'created_at')
    search_fields = ('reference_number', 'user__username', 'title')
    list_filter = ('status', 'created_at')