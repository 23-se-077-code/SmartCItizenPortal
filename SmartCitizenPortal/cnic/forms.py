from django import forms
from .models import CNICApplication

class Step1Form(forms.ModelForm):
    class Meta:
        model = CNICApplication
        fields = [
            'full_name', 'father_name', 'father_cnic', 'mother_name', 'mother_cnic',
            'date_of_birth', 'gender', 'nationality', 'religion', 'marital_status',
            'place_of_birth', 'blood_group', 'domicile', 'district'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890123'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890123'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'domicile': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
        }

class Step2Form(forms.ModelForm):
    class Meta:
        model = CNICApplication
        fields = [
            'cnic_number', 'permanent_address', 'same_as_permanent',
            'current_address', 'city', 'district_address', 'province',
            'postal_code', 'phone', 'email', 'emergency_contact',
            'application_type'
        ]
        widgets = {
            'permanent_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'current_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'same_as_permanent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'application_type': forms.Select(attrs={'class': 'form-control'}),
            'cnic_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890123'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'district_address': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }

class Step3Form(forms.ModelForm):
    class Meta:
        model = CNICApplication
        fields = ['photo', 'signature', 'left_thumb', 'right_thumb']