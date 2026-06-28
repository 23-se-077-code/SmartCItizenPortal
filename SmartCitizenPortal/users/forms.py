from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from datetime import date
import re

class CustomUserCreationForm(UserCreationForm):
    cnic = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 42101-1234567-8'})
    )
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '03XX-XXXXXXX'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Your full address'}),
        required=False
    )
    province = forms.ChoiceField(
        choices=[
            ('', 'Select Province'),
            ('IS', 'Islamabad'),
            ('PB', 'Punjab'),
            ('SD', 'Sindh'),
            ('KP', 'Khyber Pakhtunkhwa'),
            ('BL', 'Balochistan'),
            ('GB', 'Gilgit Baltistan'),
            ('AJK', 'Kashmir'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    live_selfie_data = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'cnic', 'date_of_birth', 'phone', 'address', 'province']

    def clean_cnic(self):
        cnic = self.cleaned_data.get('cnic')
        if not re.match(r'^\d{5}-\d{7}-\d{1}$', cnic):
            raise forms.ValidationError('CNIC format must be #####-#######-#')
        # Optional CNIC verification API call (uncomment when ready)
        # import requests
        # response = requests.get(f'https://api.cnicverifier.gov.pk/verify/{cnic}')
        # if response.status_code != 200 or not response.json().get('valid'):
        #     raise forms.ValidationError('Invalid CNIC number.')
        if UserProfile.objects.filter(cnic=cnic).exists():
            raise forms.ValidationError('CNIC already registered.')
        return cnic

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise forms.ValidationError('You must be at least 18 years old to register.')
        return dob

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.cnic = self.cleaned_data['cnic']
            profile.date_of_birth = self.cleaned_data['date_of_birth']
            profile.phone = self.cleaned_data.get('phone', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.province = self.cleaned_data.get('province', '')
            if profile.date_of_birth:
                today = date.today()
                profile.age = today.year - profile.date_of_birth.year - ((today.month, today.day) < (profile.date_of_birth.month, profile.date_of_birth.day))
            # Save live selfie
            live_selfie_data = self.cleaned_data.get('live_selfie_data')
            if live_selfie_data and ',' in live_selfie_data:
                import base64
                from django.core.files.base import ContentFile
                fmt, imgstr = live_selfie_data.split(';base64,')
                ext = fmt.split('/')[-1]
                profile.selfie = ContentFile(base64.b64decode(imgstr), name=f"selfie_{user.id}.{ext}")
            profile.save()
        return user