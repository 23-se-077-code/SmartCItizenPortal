from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Province(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=5, unique=True)
    def __str__(self): return self.name

class AssemblyType(models.Model):
    code = models.CharField(max_length=10)  # NA, PP, PS, PK, PB, PG, PKS
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="assemblies")
    class Meta:
        unique_together = ('code', 'province')
    def __str__(self): return f"{self.province.code}-{self.code}"

class Constituency(models.Model):
    code = models.CharField(max_length=20, unique=True)  # e.g., NA-52, PP-11
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    assembly = models.ForeignKey(AssemblyType, on_delete=models.CASCADE, related_name="constituencies")
    def __str__(self): return self.code

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    party = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="candidates/", blank=True, null=True)
    symbol = models.ImageField(upload_to="symbols/", blank=True, null=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name="candidates")
    votes = models.IntegerField(default=0)
    def __str__(self): return self.name

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("user", "constituency")
    def __str__(self):
        return f"{self.user.username} → {self.candidate.name} in {self.constituency.code}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voting_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    selfie = models.ImageField(upload_to='selfies/', blank=True, null=True)
    cnic_photo = models.ImageField(upload_to='cnic_photos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Strictly ties voters to specific geographic boundaries
    assigned_na_constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True, related_name='na_voters')
    assigned_pa_constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True, related_name='pa_voters')

    def is_eligible(self):
        if not self.date_of_birth: return False
        today = date.today()
        age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age >= 18

    def __str__(self):
        return f"{self.user.username}'s profile"