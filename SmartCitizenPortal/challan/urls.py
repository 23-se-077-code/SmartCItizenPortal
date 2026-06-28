from django.urls import path
from . import views

app_name = 'challan'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bills/', views.bill_list, name='bill_list'),
    path('challans/', views.challan_list, name='challan_list'),

    # Bill payment steps
    path('pay-bill/', views.pay_bill_step1, name='pay_bill_step1'),
    path('pay-bill/<slug:category_slug>/', views.pay_bill_step2, name='pay_bill_step2'),
    path('pay-bill/confirm/<int:bill_id>/', views.pay_bill_confirm, name='pay_bill_confirm'),

    # Challan payment steps
    path('pay-challan/', views.pay_challan_step1, name='pay_challan_step1'),
    path('pay-challan/<slug:category_slug>/', views.pay_challan_step2, name='pay_challan_step2'),
    path('pay-challan/confirm/<int:challan_id>/', views.pay_challan_confirm, name='pay_challan_confirm'),

    # JazzCash
    path('jazzcash/redirect/<int:bill_id>/', views.jazzcash_redirect, name='jazzcash_bill'),
    path('jazzcash/redirect/challan/<int:challan_id>/', views.jazzcash_redirect, name='jazzcash_challan'),
    path('jazzcash/return/', views.jazzcash_return, name='jazzcash_return'),

    # EasyPaisa
    path('easypaisa/redirect/<int:bill_id>/', views.easypaisa_redirect, name='easypaisa_bill'),
    path('easypaisa/redirect/challan/<int:challan_id>/', views.easypaisa_redirect, name='easypaisa_challan'),
    path('easypaisa/return/', views.easypaisa_return, name='easypaisa_return'),

    # Application fee payment
    path('pay-application/<str:app_type>/<int:app_id>/', views.pay_application_fee, name='pay_application_fee'),

    # Success & History
    path('success/<str:transaction_id>/', views.payment_success, name='payment_success'),
    path('history/', views.payment_history, name='history'),
]