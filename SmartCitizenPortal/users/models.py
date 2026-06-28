from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cnic = models.CharField(max_length=15, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    province = models.CharField(max_length=50, null=True, blank=True)
    selfie = models.ImageField(upload_to='selfies/', blank=True, null=True)

    # Voting fields (if needed)
    constituency_na = models.ForeignKey('voting.Constituency', on_delete=models.SET_NULL, null=True, blank=True, related_name='voters_na')
    constituency_pa = models.ForeignKey('voting.Constituency', on_delete=models.SET_NULL, null=True, blank=True, related_name='voters_pa')
    has_voted_na = models.BooleanField(default=False)
    has_voted_pa = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username