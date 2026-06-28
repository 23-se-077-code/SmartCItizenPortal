import base64
import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import JsonResponse
from formtools.wizard.views import SessionWizardView
from .models import Citizen, Address, FamilyMember
from .forms import Step1Form, Step2Form, Step3Form

def save_base64_image(base64_str, prefix):
    if not base64_str:
        return None
    try:
        format, imgstr = base64_str.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'{prefix}_{uuid.uuid4()}.{ext}')
        return data
    except Exception:
        return None

class CitizenWizardView(SessionWizardView):
    form_list = [Step1Form, Step2Form, Step3Form]
    template_name = 'citizens/wizard.html'

    def done(self, form_list, **kwargs):
        citizen_data = form_list[0].cleaned_data
        citizen = Citizen.objects.create(user=self.request.user, **citizen_data)

        address_data = form_list[1].cleaned_data
        Address.objects.create(citizen=citizen, **address_data)

        family_data = form_list[2].cleaned_data
        FamilyMember.objects.create(citizen=citizen, **family_data)

        # Save captured images if any
        face_b64 = self.request.POST.get('face_image_base64')
        fingerprint_b64 = self.request.POST.get('fingerprint_image_base64')
        if face_b64:
            citizen.photo = save_base64_image(face_b64, 'face')
        if fingerprint_b64:
            citizen.fingerprint = save_base64_image(fingerprint_b64, 'finger')
        citizen.status = 'SUBMITTED'
        citizen.save()

        messages.success(self.request, 'Citizen application submitted successfully!')
        return redirect('citizens:dashboard')

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        context['step'] = self.steps.step1
        context['total_steps'] = 3
        return context

@login_required
def citizen_dashboard(request):
    citizens = Citizen.objects.filter(user=request.user)
    return render(request, 'citizens/dashboard.html', {'citizens': citizens})

@login_required
def view_citizen(request, pk):
    citizen = Citizen.objects.get(pk=pk, user=request.user)
    return render(request, 'citizens/view.html', {'citizen': citizen})