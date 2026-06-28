from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from formtools.wizard.views import SessionWizardView
from datetime import date
from .models import CNICApplication
from .forms import Step1Form, Step2Form, Step3Form

FORMS = [("personal", Step1Form), ("address", Step2Form), ("documents", Step3Form)]
TEMPLATES = {
    "personal": "cnic/step1.html",
    "address": "cnic/step2.html",
    "documents": "cnic/step3.html",
}

class CNICWizard(SessionWizardView):
    form_list = FORMS
    template_name = "cnic/wizard.html"
    file_storage = FileSystemStorage()

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = {}
        for form in form_list:
            form_data.update(form.cleaned_data)

        # Age verification
        dob = form_data.get('date_of_birth')
        if dob:
            age = (date.today() - dob).days // 365
            if age < 18:
                messages.error(self.request, "You must be at least 18 years old to apply for CNIC.")
                return redirect('cnic_apply')

        # CNIC uniqueness
        cnic = form_data.get('cnic_number')
        if CNICApplication.objects.filter(cnic_number=cnic).exists():
            messages.error(self.request, "This CNIC number is already registered.")
            return redirect('cnic_apply')

        # Validate father/mother CNIC format (13 digits)
        father_cnic = form_data.get('father_cnic')
        if father_cnic and (not father_cnic.isdigit() or len(father_cnic) != 13):
            messages.error(self.request, "Father's CNIC must be exactly 13 digits.")
            return redirect('cnic_apply')
        mother_cnic = form_data.get('mother_cnic')
        if mother_cnic and (not mother_cnic.isdigit() or len(mother_cnic) != 13):
            messages.error(self.request, "Mother's CNIC must be exactly 13 digits.")
            return redirect('cnic_apply')

        # Create application
        app = CNICApplication(user=self.request.user, **form_data)
        for field in ['photo', 'signature', 'left_thumb', 'right_thumb']:
            if field in self.request.FILES:
                setattr(app, field, self.request.FILES[field])
        app.status = 'SUBMITTED'
        app.save()

        messages.success(self.request, f"CNIC application submitted. Your ID: {app.application_id}")
        return redirect('cnic_dashboard')

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        context['step_index'] = self.steps.step0
        context['total_steps'] = len(self.form_list)
        return context

@login_required
def dashboard(request):
    apps = CNICApplication.objects.filter(user=request.user).order_by('-created_at')
    total = apps.count()
    approved = apps.filter(status='APPROVED').count()
    pending = apps.filter(status__in=['SUBMITTED', 'UNDER_VERIFICATION']).count()
    return render(request, 'cnic/dashboard.html', {
        'applications': apps,
        'total': total,
        'approved': approved,
        'pending': pending,
    })

@login_required
def status_view(request, app_id):
    app = get_object_or_404(CNICApplication, id=app_id, user=request.user)
    return render(request, 'cnic/status.html', {'app': app})