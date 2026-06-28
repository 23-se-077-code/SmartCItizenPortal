from django.urls import path
from .views import CitizenWizardView, citizen_dashboard, view_citizen

app_name = 'citizens'

urlpatterns = [
    path('apply/', CitizenWizardView.as_view(), name='apply'),
    path('dashboard/', citizen_dashboard, name='dashboard'),
    path('view/<int:pk>/', view_citizen, name='view'),
]
