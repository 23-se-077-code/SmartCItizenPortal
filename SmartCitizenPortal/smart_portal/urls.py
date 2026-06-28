from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin System Interface Route Descriptor
    path('admin/', admin.site.urls),

    # Identity Management Modules
    path('users/', include('users.urls')),
    path('cnic/', include('cnic.urls')),
    path('passport/', include('passport.urls')),

    # Citizen Services
    path('complaints/', include('complaints.urls')),
    path('voting/', include('voting.urls')),
    path('challan/', include('challan.urls')),
    path('citizens/', include('citizens.urls')),
]

# This compiles static media routing allocations cleanly in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)