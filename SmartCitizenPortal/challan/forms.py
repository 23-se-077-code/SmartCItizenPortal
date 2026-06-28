from django import forms
from .models import Bill, Challan

class BillPaymentForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['consumer_number', 'consumer_name', 'amount', 'due_date', 'bill_image']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'consumer_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CNS-12345'}),
            'consumer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bill_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['bill_image'].required = False

class ChallanPaymentForm(forms.ModelForm):
    class Meta:
        model = Challan
        fields = ['challan_number', 'citizen_name', 'cnic', 'amount', 'due_date', 'area', 'description', 'payment_screenshot']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'challan_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CH-12345'}),
            'citizen_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '42101-1234567-1'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Lahore'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'payment_screenshot': forms.FileInput(attrs={'class': 'form-control'}),
        }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['payment_screenshot'].required = False
            self.fields['area'].required = False
            self.fields['description'].required = False