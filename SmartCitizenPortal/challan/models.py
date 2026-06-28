from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid

class BillCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    def __str__(self): return self.name

class ChallanCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    def __str__(self): return self.name

class Bill(models.Model):
    STATUS_CHOICES = (('unpaid', 'Unpaid'), ('paid', 'Paid'), ('overdue', 'Overdue'))
    consumer_number = models.CharField(max_length=50)
    consumer_name = models.CharField(max_length=200)
    category = models.ForeignKey(BillCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    bill_image = models.ImageField(upload_to='bills/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.consumer_name} - {self.category.name}"

class Challan(models.Model):
    STATUS_CHOICES = (('unpaid', 'Unpaid'), ('paid', 'Paid'))
    challan_number = models.CharField(max_length=20, unique=True, default=uuid.uuid4().hex[:10].upper())
    citizen_name = models.CharField(max_length=200)
    cnic = models.CharField(max_length=15)
    category = models.ForeignKey(ChallanCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    description = models.TextField(blank=True)
    area = models.CharField(max_length=100, blank=True)
    payment_screenshot = models.ImageField(upload_to='challan_payments/', blank=True, null=True)
    def __str__(self): return f"{self.challan_number} - {self.citizen_name}"

class PaymentTransaction(models.Model):
    PAYMENT_TYPES = (
        ('bill', 'Bill Payment'),
        ('challan', 'Challan Payment'),
        ('application', 'Application Fee'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=15, choices=PAYMENT_TYPES)
    bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, null=True, blank=True)
    challan = models.ForeignKey(Challan, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=20, unique=True, default=uuid.uuid4().hex[:12].upper())
    paid_at = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_name = models.CharField(max_length=20, blank=True, null=True)
    # Application fee fields
    app_type = models.CharField(max_length=20, blank=True)
    app_id = models.IntegerField(null=True, blank=True)
    reference_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.user.username} - {self.amount}"