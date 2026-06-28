from django.contrib import admin
from .models import PassportApplication, ParentInfo, SpouseInfo, Address, Document, Biometric, Payment, StatusLog

admin.site.register(PassportApplication)
admin.site.register(ParentInfo)
admin.site.register(SpouseInfo)
admin.site.register(Address)
admin.site.register(Document)
admin.site.register(Biometric)
admin.site.register(Payment)
admin.site.register(StatusLog)