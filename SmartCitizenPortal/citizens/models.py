from django.db import models
from django.contrib.auth.models import User

class Citizen(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    MARITAL_STATUS = (('S', 'Single'), ('M', 'Married'), ('D', 'Divorced'), ('W', 'Widowed'))
    STATUS_CHOICES = (('DRAFT', 'Draft'), ('SUBMITTED', 'Submitted'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'))

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='citizen_profile')
    full_name = models.CharField(max_length=255)
    cnic = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    nationality = models.CharField(max_length=100, default='Pakistan')
    photo = models.ImageField(upload_to='citizen_photos/', blank=True, null=True)
    fingerprint = models.ImageField(upload_to='citizen_fingerprints/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.cnic})"

class Household(models.Model):
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='households')
    household_head = models.CharField(max_length=255)
    head_cnic = models.CharField(max_length=15)
    total_members = models.IntegerField()
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    is_bpl = models.BooleanField(default=False)

    def __str__(self):
        return f"Household of {self.household_head}"

class Address(models.Model):
    ADDRESS_TYPES = (('current', 'Current'), ('permanent', 'Permanent'))
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_address_type_display()} Address of {self.citizen.full_name}"

class FamilyMember(models.Model):
    RELATION_TYPES = (('spouse', 'Spouse'), ('child', 'Child'), ('parent', 'Parent'), ('sibling', 'Sibling'))
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='family_members')
    relation_type = models.CharField(max_length=10, choices=RELATION_TYPES)
    full_name = models.CharField(max_length=255)
    cnic = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField()
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.get_relation_type_display()} of {self.citizen.full_name})"

class Document(models.Model):
    DOC_TYPES = (('cnic', 'CNIC Scan'), ('proof_of_address', 'Proof of Address'), ('birth_certificate', 'Birth Certificate'), ('other', 'Other'))
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOC_TYPES)
    file = models.FileField(upload_to='citizen_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.citizen.full_name}"

class Application(models.Model):
    APP_TYPES = (('citizenship', 'Citizenship Registration'), ('id_card', 'ID Card Renewal'), ('family_registration', 'Family Registration'), ('other', 'Other'))
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='applications')
    application_type = models.CharField(max_length=20, choices=APP_TYPES)
    status = models.CharField(max_length=20, choices=Citizen.STATUS_CHOICES, default='SUBMITTED')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    admin_remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_application_type_display()} - {self.citizen.full_name}"