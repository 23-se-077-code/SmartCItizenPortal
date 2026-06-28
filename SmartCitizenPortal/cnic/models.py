from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date, timedelta
import uuid
import qrcode
from io import BytesIO
from django.core.files import File

class CNICApplication(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_VERIFICATION', 'Under Verification'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    APPLICATION_TYPE = [
        ('NORMAL', 'Normal (PKR 700)'),
        ('URGENT', 'Urgent (PKR 2500)'),
    ]
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    MARITAL_CHOICES = [('S', 'Single'), ('M', 'Married'), ('D', 'Divorced'), ('W', 'Widowed')]

    application_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Personal Information
    full_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    father_cnic = models.CharField(
        max_length=13,
        validators=[RegexValidator(r'^\d{13}$', 'CNIC must be 13 digits without dashes')],
        blank=True, null=True
    )
    mother_name = models.CharField(max_length=100, blank=True)
    mother_cnic = models.CharField(
        max_length=13,
        validators=[RegexValidator(r'^\d{13}$', 'CNIC must be 13 digits without dashes')],
        blank=True, null=True
    )
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=50, default='Pakistani')
    religion = models.CharField(max_length=50, blank=True)
    marital_status = models.CharField(max_length=1, choices=MARITAL_CHOICES)
    place_of_birth = models.CharField(max_length=100, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    domicile = models.CharField(max_length=50, blank=True)
    district = models.CharField(max_length=50, blank=True)

    # CNIC Identity
    cnic_number = models.CharField(
        max_length=13,
        unique=True,
        validators=[RegexValidator(r'^\d{13}$', 'CNIC must be 13 digits without dashes')]
    )

    # Address
    permanent_address = models.TextField()
    current_address = models.TextField(blank=True)
    same_as_permanent = models.BooleanField(default=True)
    city = models.CharField(max_length=50)
    district_address = models.CharField(max_length=50, blank=True)
    province = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)

    # Contact
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    # Application Details
    application_type = models.CharField(max_length=10, choices=APPLICATION_TYPE, default='NORMAL')
    fee = models.IntegerField(default=700)

    # Biometrics
    photo = models.ImageField(upload_to='cnic/photos/', blank=True, null=True)
    signature = models.ImageField(upload_to='cnic/signatures/', blank=True, null=True)
    left_thumb = models.ImageField(upload_to='cnic/thumbs/', blank=True, null=True)
    right_thumb = models.ImageField(upload_to='cnic/thumbs/', blank=True, null=True)

    # Status and Generated CNIC
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    generated_cnic = models.CharField(max_length=13, unique=True, blank=True, null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    tracking_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    qr_code = models.ImageField(upload_to='cnic/qrcodes/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.application_id:
            self.application_id = f"CNIC-{uuid.uuid4().hex[:8].upper()}"

        self.fee = 2500 if self.application_type == 'URGENT' else 700

        if not self.tracking_number and self.status != 'DRAFT':
            self.tracking_number = f"TRK-{uuid.uuid4().hex[:6].upper()}"

        if self.status == 'APPROVED' and not self.generated_cnic:
            self.generated_cnic = self.generate_cnic_number()
            self.issue_date = date.today()
            self.expiry_date = date.today() + timedelta(days=365*10)
            self.generate_qr_code()

        super().save(*args, **kwargs)

    def generate_cnic_number(self):
        import random
        a = str(random.randint(10000, 99999))
        b = str(random.randint(1000000, 9999999))
        c = str(random.randint(1, 9))
        return f"{a}-{b}-{c}"

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(f"CNIC:{self.generated_cnic}|App:{self.application_id}")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        self.qr_code.save(f"qr_{self.application_id}.png", File(buffer), save=False)

    def __str__(self):
        return f"{self.full_name} - {self.application_id}"