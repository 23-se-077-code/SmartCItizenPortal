from django.urls import path
from .views import CNICWizard, dashboard, status_view

urlpatterns = [
    path('', dashboard, name='cnic_dashboard'),
    path('apply/', CNICWizard.as_view(), name='cnic_apply'),
    path('status/<int:app_id>/', status_view, name='cnic_status'),
]