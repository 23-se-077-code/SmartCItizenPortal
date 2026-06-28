from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='passport_dashboard'),
    path('apply/<int:step>/', views.apply_passport, name='passport_apply_step'),
    path('apply/', views.apply_passport, {'step': 1}, name='passport_apply'),
    path('track/<int:app_id>/', views.track_application, name='passport_track'),
    path('receipt/<int:app_id>/', views.receipt, name='passport_receipt'),
    path('admin/', views.admin_panel, name='passport_admin_panel'),
    path('update/<int:app_id>/<str:status>/', views.update_status, name='passport_update_status'),
    path('view/<int:app_id>/', views.view_passport, name='passport_view'),
]