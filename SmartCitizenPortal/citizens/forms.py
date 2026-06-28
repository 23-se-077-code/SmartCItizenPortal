from django import forms
from .models import Citizen, Address, FamilyMember, Household

class Step1Form(forms.ModelForm):
    class Meta:
        model = Citizen
        fields = ['full_name', 'cnic', 'date_of_birth', 'gender', 'marital_status', 'phone', 'email', 'nationality']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
        }

class Step2Form(forms.Form):
    address_type = forms.ChoiceField(choices=Address.ADDRESS_TYPES, widget=forms.Select(attrs={'class': 'form-control'}))
    street = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    district = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    province = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

class Step3Form(forms.Form):
    relation_type = forms.ChoiceField(choices=FamilyMember.RELATION_TYPES, widget=forms.Select(attrs={'class': 'form-control'}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    cnic = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))