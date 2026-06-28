from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date, timedelta
import random
import qrcode
from io import BytesIO
from django.core.files import File

class PassportApplication(models.Model):
    application_id = models.CharField(max_length=20, unique=True, editable=False)
    application_date = models.DateTimeField(auto_now_add=True)

    CATEGORY_CHOICES = [
        ('NEW', 'New Passport'),
        ('RENEW', 'Renewal'),
        ('LOST', 'Lost'),
        ('DAMAGED', 'Damaged'),
    ]
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='NEW')

    PROCESSING_CHOICES = [
        ('ORDINARY', 'Ordinary (PKR 5,000)'),
        ('URGENT', 'Urgent (PKR 10,000)'),
    ]
    processing_type = models.CharField(max_length=10, choices=PROCESSING_CHOICES, default='ORDINARY')

    PAGE_CHOICES = [
        (36, '36 Pages'),
        (72, '72 Pages (+PKR 2,000)'),
        (100, '100 Pages (+PKR 4,000)'),
    ]
    pages = models.IntegerField(choices=PAGE_CHOICES, default=36)

    full_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('M','Male'),('F','Female'),('O','Other')])
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    nationality = models.CharField(max_length=50, default='Pakistani')
    religion = models.CharField(max_length=50, blank=True)
    marital_status = models.CharField(max_length=20, choices=[('S','Single'),('M','Married'),('D','Divorced'),('W','Widowed')])
    blood_group = models.CharField(max_length=5, blank=True)
    height = models.CharField(max_length=10, blank=True)
    eye_color = models.CharField(max_length=20, blank=True)
    identification_marks = models.TextField(blank=True)

    cnic = models.CharField(max_length=15, unique=True, validators=[RegexValidator(r'^\d{5}-\d{7}-\d$', 'Invalid CNIC format')])
    cnic_issue_date = models.DateField()
    cnic_expiry_date = models.DateField()
    family_registration_number = models.CharField(max_length=20, blank=True)
    b_form_number = models.CharField(max_length=20, blank=True)

    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=15)
    emergency_relationship = models.CharField(max_length=50)

    highest_qualification = models.CharField(max_length=100, blank=True)
    institute_name = models.CharField(max_length=200, blank=True)
    passing_year = models.IntegerField(null=True, blank=True)

    employment_status = models.CharField(max_length=20, choices=[('EMP','Employed'),('UNEMP','Unemployed'),('STU','Student')], default='UNEMP')
    occupation = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    monthly_income = models.CharField(max_length=50, blank=True)

    travel_purpose = models.CharField(max_length=50, choices=[('TOURISM','Tourism'),('STUDY','Study'),('WORK','Work'),('BUSINESS','Business'),('RELIGIOUS','Religious')], default='TOURISM')
    destination_country = models.CharField(max_length=100, blank=True)
    expected_travel_date = models.DateField(null=True, blank=True)
    previous_passport_number = models.CharField(max_length=20, blank=True)

    fee = models.IntegerField(default=5000)

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('DOC_VERIFIED', 'Documents Verified'),
        ('BIO_VERIFIED', 'Biometric Verified'),
        ('APPROVED', 'Approved'),
        ('PRINTING', 'Printing'),
        ('DISPATCHED', 'Dispatched'),
        ('DELIVERED', 'Delivered'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    passport_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    # Tracking & QR Code (NEW)
    tracking_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    qr_code = models.ImageField(upload_to='passport/qrcodes/', null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.application_id:
            year = date.today().year
            rand = str(random.randint(1000, 9999))
            self.application_id = f"PP-{year}-{rand}"
        
        # Fee calculation
        fee = 5000 if self.processing_type == 'ORDINARY' else 10000
        if self.pages == 72:
            fee += 2000
        elif self.pages == 100:
            fee += 4000
        self.fee = fee

        # Generate tracking number
        if not self.tracking_number and self.status != 'DRAFT':
            self.tracking_number = f"TRK-{random.randint(100000, 999999)}"

        # Generate passport number & dates on approval
        if self.status == 'APPROVED' and not self.passport_number:
            self.passport_number = f"PK-{date.today().year}-{random.randint(100000, 999999)}"
            self.issue_date = date.today()
            self.expiry_date = date.today() + timedelta(days=365*10)  # 10 years
            self.generate_qr_code()

        super().save(*args, **kwargs)

    def generate_qr_code(self):
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(f"PASSPORT:{self.passport_number}|App:{self.application_id}")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        self.qr_code.save(f"qr_{self.application_id}.png", File(buffer), save=False)

    def __str__(self):
        return f"{self.full_name} - {self.application_id}"

# -------------------------------------------------------------------
# ParentInfo, SpouseInfo, Address, Document, Biometric, Payment, StatusLog
# remain unchanged – they are already correct.
# -------------------------------------------------------------------

class ParentInfo(models.Model):
    application = models.OneToOneField(PassportApplication, on_delete=models.CASCADE, related_name='parents')
    father_name = models.CharField(max_length=200)
    father_cnic = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{5}-\d{7}-\d$', 'Invalid CNIC')])
    father_occupation = models.CharField(max_length=100, blank=True)
    father_contact = models.CharField(max_length=15, blank=True)
    mother_name = models.CharField(max_length=200)
    mother_cnic = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{5}-\d{7}-\d$', 'Invalid CNIC')])
    mother_occupation = models.CharField(max_length=100, blank=True)
    mother_contact = models.CharField(max_length=15, blank=True)

class SpouseInfo(models.Model):
    application = models.OneToOneField(PassportApplication, on_delete=models.CASCADE, related_name='spouse', null=True, blank=True)
    spouse_name = models.CharField(max_length=200, blank=True)
    spouse_cnic = models.CharField(max_length=15, blank=True, validators=[RegexValidator(r'^\d{5}-\d{7}-\d$', 'Invalid CNIC')])
    marriage_date = models.DateField(null=True, blank=True)

class Address(models.Model):
    application = models.OneToOneField(PassportApplication, on_delete=models.CASCADE, related_name='address')
    perm_house = models.CharField(max_length=50)
    perm_street = models.CharField(max_length=100)
    perm_area = models.CharField(max_length=100)
    perm_city = models.CharField(max_length=50)
    perm_district = models.CharField(max_length=50)
    perm_province = models.CharField(max_length=50)
    perm_postal = models.CharField(max_length=10)
    same_as_permanent = models.BooleanField(default=True)
    curr_house = models.CharField(max_length=50, blank=True)
    curr_street = models.CharField(max_length=100, blank=True)
    curr_area = models.CharField(max_length=100, blank=True)
    curr_city = models.CharField(max_length=50, blank=True)
    curr_district = models.CharField(max_length=50, blank=True)
    curr_province = models.CharField(max_length=50, blank=True)
    curr_postal = models.CharField(max_length=10, blank=True)

class Document(models.Model):
    application = models.ForeignKey(PassportApplication, on_delete=models.CASCADE, related_name='documents')
    DOC_TYPES = [
        ('CNIC_FRONT', 'CNIC Front'),
        ('CNIC_BACK', 'CNIC Back'),
        ('PHOTO', 'Passport Size Photo'),
        ('BIRTH_CERT', 'Birth Certificate'),
        ('UTILITY_BILL', 'Utility Bill'),
        ('PREV_PASSPORT', 'Previous Passport Copy'),
        ('MARRIAGE_CERT', 'Marriage Certificate'),
        ('EDU_CERT', 'Educational Certificate'),
    ]
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)
    file = models.FileField(upload_to='passport/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

class Biometric(models.Model):
    application = models.OneToOneField(PassportApplication, on_delete=models.CASCADE, related_name='biometric')
    photo = models.ImageField(upload_to='passport/photos/', null=True, blank=True)
    signature = models.ImageField(upload_to='passport/signatures/', null=True, blank=True)
    left_thumb = models.ImageField(upload_to='passport/fingerprints/', null=True, blank=True)
    right_thumb = models.ImageField(upload_to='passport/fingerprints/', null=True, blank=True)
    verified = models.BooleanField(default=False)

class Payment(models.Model):
    application = models.OneToOneField(PassportApplication, on_delete=models.CASCADE, related_name='payment')
    amount = models.IntegerField()
    payment_method = models.CharField(max_length=50, default='Simulated')
    transaction_id = models.CharField(max_length=100, blank=True)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

class StatusLog(models.Model):
    application = models.ForeignKey(PassportApplication, on_delete=models.CASCADE, related_name='status_logs')
    status = models.CharField(max_length=20, choices=PassportApplication.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)