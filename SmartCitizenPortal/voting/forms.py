from django import forms
from .models import UserProfile, Province, AssemblyType, Constituency, Candidate

class BiometricVerificationForm(forms.Form):
    cnic_photo = forms.ImageField(
        label="CNIC Front Image File", 
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    live_selfie_data = forms.CharField(widget=forms.HiddenInput(), required=True)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['date_of_birth']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'true'})}

class ProvinceForm(forms.Form):
    province = forms.ModelChoiceField(
        queryset=Province.objects.all(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None
    )

class AssemblyForm(forms.Form):
    assembly = forms.ModelChoiceField(
        queryset=AssemblyType.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None
    )
    def __init__(self, *args, **kwargs):
        province_id = kwargs.pop("province_id", None)
        super().__init__(*args, **kwargs)
        if province_id:
            self.fields["assembly"].queryset = AssemblyType.objects.filter(province_id=province_id)

class ConstituencyForm(forms.Form):
    constituency = forms.ModelChoiceField(
        queryset=Constituency.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None
    )
    def __init__(self, *args, **kwargs):
        assembly_id = kwargs.pop("assembly_id", None)
        super().__init__(*args, **kwargs)
        if assembly_id:
            self.fields["constituency"].queryset = Constituency.objects.filter(assembly_id=assembly_id)

class CandidateForm(forms.Form):
    candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None
    )
    def __init__(self, *args, **kwargs):
        constituency_id = kwargs.pop("constituency_id", None)
        super().__init__(*args, **kwargs)
        if constituency_id:
            self.fields["candidate"].queryset = Candidate.objects.filter(constituency_id=constituency_id)