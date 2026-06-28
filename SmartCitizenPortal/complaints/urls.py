from django.urls import path
from . import views

urlpatterns = [
    path('', views.complaint_list, name='complaints'),
    path('add/', views.add_complaint, name='add_complaint'),
]