# passport/forms.py

from django import forms
from django.core.validators import RegexValidator
from .models import PassportApplication, Address, Biometric

class Step1PersonalForm(forms.ModelForm):
    class Meta:
        model = PassportApplication
        fields = [
            'category', 'processing_type', 'pages',
            'full_name', 'first_name', 'last_name', 'gender', 'date_of_birth',
            'place_of_birth', 'nationality', 'religion', 'marital_status',
            'blood_group', 'height', 'eye_color', 'identification_marks',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Muhammad Ali Khan'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City/Town'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nationality'}),
            'religion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Religion'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B+'}),
            'height': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5 ft 10 in'}),
            'eye_color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Brown'}),
            'identification_marks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Any visible marks'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'processing_type': forms.Select(attrs={'class': 'form-control'}),
            'pages': forms.Select(attrs={'class': 'form-control'}),
        }

class Step2IdentityForm(forms.ModelForm):
    class Meta:
        model = PassportApplication
        fields = ['cnic', 'cnic_issue_date', 'cnic_expiry_date',
                  'family_registration_number', 'b_form_number']
        widgets = {
            'cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345-1234567-1'}),
            'cnic_issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cnic_expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'family_registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'b_form_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        }

class Step3ParentSpouseForm(forms.Form):
    father_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Full Name"}))
    father_cnic = forms.CharField(max_length=15, validators=[RegexValidator(r'^\d{5}-\d{7}-\d$', 'Invalid CNIC format')],
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345-1234567-1'}))
    father_occupation = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Occupation'}))
    father_contact = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '03XX-XXXXXXX'}))
    mother_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Full Name"}))
    mother_cnic = forms.CharField(max_length=15, validators=[RegexValidator(r'^\d{5}-\d{7}-\d$', 'Invalid CNIC format')],
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345-1234567-1'}))
    mother_occupation = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Occupation'}))
    mother_contact = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '03XX-XXXXXXX'}))
    spouse_name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Spouse Name'}))
    spouse_cnic = forms.CharField(max_length=15, required=False, validators=[RegexValidator(r'^\d{5}-\d{7}-\d$', 'Invalid CNIC')],
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345-1234567-1'}))
    marriage_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

class Step4AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['application']
        widgets = {
            'perm_house': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'House #'}),
            'perm_street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street'}),
            'perm_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Area/Sector'}),
            'perm_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'perm_district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District'}),
            'perm_province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Province'}),
            'perm_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'same_as_permanent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'curr_house': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'House #'}),
            'curr_street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street'}),
            'curr_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Area/Sector'}),
            'curr_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'curr_district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District'}),
            'curr_province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Province'}),
            'curr_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
        }

class Step5EducationEmploymentTravelForm(forms.ModelForm):
    class Meta:
        model = PassportApplication
        fields = [
            'highest_qualification', 'institute_name', 'passing_year',
            'employment_status', 'occupation', 'organization', 'monthly_income',
            'travel_purpose', 'destination_country', 'expected_travel_date',
            'previous_passport_number',
            # --- CONTACT FIELDS ---
            'mobile', 'email',
            'emergency_contact_name', 'emergency_contact_number', 'emergency_relationship',
        ]
        widgets = {
            'expected_travel_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'highest_qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bachelor\'s'}),
            'institute_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'University/Institute'}),
            'passing_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'YYYY'}),
            'employment_status': forms.Select(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company/Organization'}),
            'monthly_income': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PKR'}),
            'travel_purpose': forms.Select(attrs={'class': 'form-control'}),
            'destination_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country Name'}),
            'previous_passport_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'If any'}),
            # Contact widgets
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '03XX-XXXXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'emergency_contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '03XX-XXXXXXX'}),
            'emergency_relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Brother, Father'}),
        }

class Step6DocumentUploadForm(forms.Form):
    cnic_front = forms.FileField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))
    cnic_back = forms.FileField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))
    photo = forms.FileField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))
    birth_cert = forms.FileField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))
    utility_bill = forms.FileField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))
    prev_passport = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    marriage_cert = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    edu_cert = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

class Step7BiometricForm(forms.ModelForm):
    class Meta:
        model = Biometric
        fields = ['photo', 'signature', 'left_thumb', 'right_thumb']