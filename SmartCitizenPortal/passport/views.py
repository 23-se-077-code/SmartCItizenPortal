import base64
import uuid
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db import IntegrityError
from .models import PassportApplication, ParentInfo, SpouseInfo, Address, Document, Biometric, Payment, StatusLog
from .forms import (
    Step1PersonalForm, Step2IdentityForm, Step3ParentSpouseForm,
    Step4AddressForm, Step5EducationEmploymentTravelForm,
    Step6DocumentUploadForm, Step7BiometricForm
)

def staff_check(user):
    return user.is_staff

# ---------- HELPER: Convert dates in dict to strings ----------
def serialize_dates(data):
    """Recursively convert all date/datetime objects in a dict to ISO strings."""
    for key, value in data.items():
        if isinstance(value, (date, datetime)):
            data[key] = value.isoformat()
        elif isinstance(value, dict):
            serialize_dates(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    serialize_dates(item)
    return data

def deserialize_dates(data):
    """Recursively convert ISO date strings back to date objects."""
    for key, value in data.items():
        if isinstance(value, str) and (
            key.endswith('_date') or key in ['date_of_birth', 'cnic_issue_date', 'cnic_expiry_date', 'expected_travel_date', 'marriage_date']
        ):
            try:
                data[key] = datetime.fromisoformat(value).date()
            except (ValueError, TypeError):
                data[key] = None
        elif isinstance(value, dict):
            deserialize_dates(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    deserialize_dates(item)
    return data

# ---------- VIEWS ----------
@login_required
def dashboard(request):
    applications = PassportApplication.objects.filter(user=request.user).order_by('-created_at')
    total = applications.count()
    approved = applications.filter(status='APPROVED').count()
    pending = applications.filter(status__in=['SUBMITTED','UNDER_REVIEW','DOC_VERIFIED','BIO_VERIFIED']).count()
    context = {
        'applications': applications,
        'total': total,
        'approved': approved,
        'pending': pending,
    }
    return render(request, 'passport/dashboard.html', context)

@login_required
def apply_passport(request, step=1):
    # --- Reset session if requested ---
    if 'reset' in request.GET:
        for key in list(request.session.keys()):
            if key.startswith('passport_'):
                del request.session[key]
        messages.success(request, 'Session cleared. Start fresh!')
        return redirect('passport_apply_step', step=1)

    if step < 1 or step > 7:
        return redirect('passport_dashboard')

    # ---------- POST ----------
    if request.method == 'POST':
        posted_step = request.POST.get('step')
        if posted_step:
            step = int(posted_step)

        # --- Special handling for step 7: convert base64 to files ---
        if step == 7:
            photo_b64 = request.POST.get('photo')
            if photo_b64:
                try:
                    format, imgstr = photo_b64.split(';base64,')
                    ext = format.split('/')[-1]
                    request.FILES['photo'] = ContentFile(base64.b64decode(imgstr), name=f'photo_{uuid.uuid4()}.{ext}')
                except (ValueError, base64.binascii.Error):
                    messages.error(request, 'Invalid photo data.')
                    return redirect('passport_apply_step', step=7)

            sig_b64 = request.POST.get('signature')
            if sig_b64:
                try:
                    format, imgstr = sig_b64.split(';base64,')
                    ext = format.split('/')[-1]
                    request.FILES['signature'] = ContentFile(base64.b64decode(imgstr), name=f'signature_{uuid.uuid4()}.{ext}')
                except (ValueError, base64.binascii.Error):
                    messages.error(request, 'Invalid signature data.')
                    return redirect('passport_apply_step', step=7)

            finger_b64 = request.POST.get('fingerprint')
            if finger_b64:
                try:
                    format, imgstr = finger_b64.split(';base64,')
                    ext = format.split('/')[-1]
                    request.FILES['left_thumb'] = ContentFile(base64.b64decode(imgstr), name=f'fingerprint_{uuid.uuid4()}.{ext}')
                except (ValueError, base64.binascii.Error):
                    messages.error(request, 'Invalid fingerprint data.')
                    return redirect('passport_apply_step', step=7)

        forms_map = {
            1: Step1PersonalForm,
            2: Step2IdentityForm,
            3: Step3ParentSpouseForm,
            4: Step4AddressForm,
            5: Step5EducationEmploymentTravelForm,
            6: Step6DocumentUploadForm,
            7: Step7BiometricForm,
        }
        FormClass = forms_map.get(step)
        if not FormClass:
            messages.error(request, 'Invalid step.')
            return redirect('passport_dashboard')

        form = FormClass(request.POST, request.FILES)

        if form.is_valid():
            # Convert cleaned data to serializable format (dates -> strings)
            cleaned = form.cleaned_data
            cleaned = serialize_dates(cleaned)

            # --- Store in session ONLY for steps 1–5 (step 6 is not stored) ---
            if step in [1, 2, 3, 4, 5]:
                request.session[f'passport_step_{step}'] = cleaned

            if step == 6:
                # --- Retrieve and merge data from steps 1–5 ---
                step1 = request.session.get('passport_step_1', {})
                step2 = request.session.get('passport_step_2', {})
                step3 = request.session.get('passport_step_3', {})
                step4 = request.session.get('passport_step_4', {})
                step5 = request.session.get('passport_step_5', {})

                # Deserialize dates
                for step_data in [step1, step2, step5]:
                    deserialize_dates(step_data)

                # Merge data
                app_data = {**step1, **step2, **step5}
                app_data['user'] = request.user

                # Validate required fields
                required_fields = ['cnic_issue_date', 'cnic_expiry_date', 'date_of_birth', 'cnic']
                for field in required_fields:
                    if field not in app_data or app_data[field] is None:
                        messages.error(request, f'Missing required field: {field}. Please go back to step 2.')
                        return redirect('passport_apply_step', step=2)

                # Check duplicate CNIC
                cnic = step2.get('cnic')
                if PassportApplication.objects.filter(cnic=cnic).exists():
                    messages.error(request, f'An application with CNIC {cnic} already exists.')
                    return redirect('passport_apply_step', step=2)

                # Create application
                try:
                    app = PassportApplication(**app_data)
                    app.save()
                except IntegrityError as e:
                    if 'cnic' in str(e):
                        messages.error(request, 'CNIC already exists in another application.')
                        return redirect('passport_apply_step', step=2)
                    raise e

                # Create parent, spouse, address
                ParentInfo.objects.create(
                    application=app,
                    father_name=step3.get('father_name'),
                    father_cnic=step3.get('father_cnic'),
                    father_occupation=step3.get('father_occupation', ''),
                    father_contact=step3.get('father_contact', ''),
                    mother_name=step3.get('mother_name'),
                    mother_cnic=step3.get('mother_cnic'),
                    mother_occupation=step3.get('mother_occupation', ''),
                    mother_contact=step3.get('mother_contact', ''),
                )
                spouse_name = step3.get('spouse_name')
                if spouse_name:
                    marriage_date = step3.get('marriage_date')
                    if isinstance(marriage_date, str):
                        try:
                            marriage_date = datetime.fromisoformat(marriage_date).date()
                        except:
                            marriage_date = None
                    SpouseInfo.objects.create(
                        application=app,
                        spouse_name=spouse_name,
                        spouse_cnic=step3.get('spouse_cnic', ''),
                        marriage_date=marriage_date,
                    )
                addr_data = {**step4}
                addr_data['application'] = app
                Address.objects.create(**addr_data)

                # Save uploaded documents
                doc_types = {
                    'cnic_front': 'CNIC_FRONT',
                    'cnic_back': 'CNIC_BACK',
                    'photo': 'PHOTO',
                    'birth_cert': 'BIRTH_CERT',
                    'utility_bill': 'UTILITY_BILL',
                    'prev_passport': 'PREV_PASSPORT',
                    'marriage_cert': 'MARRIAGE_CERT',
                    'edu_cert': 'EDU_CERT',
                }
                for field, doc_type in doc_types.items():
                    if field in request.FILES:
                        doc = Document(application=app, doc_type=doc_type, file=request.FILES[field])
                        doc.save()

                # Clear all passport_step_* session keys to avoid stale data
                for key in list(request.session.keys()):
                    if key.startswith('passport_step_'):
                        del request.session[key]

                request.session['passport_app_id'] = app.id
                return redirect('passport_apply_step', step=7)

            if step == 7:
                app_id = request.session.get('passport_app_id')
                if not app_id:
                    messages.error(request, 'No application in progress.')
                    return redirect('passport_dashboard')
                app = get_object_or_404(PassportApplication, id=app_id, user=request.user)
                biometric = form.save(commit=False)
                biometric.application = app
                biometric.save()
                app.status = 'SUBMITTED'
                app.save()
                Payment.objects.create(
                    application=app,
                    amount=app.fee,
                    payment_method='Simulated',
                    paid=True,
                    paid_at=date.today()
                )
                StatusLog.objects.create(application=app, status='SUBMITTED', notes='Application submitted by user')
                messages.success(request, f'Passport application submitted. ID: {app.application_id}')
                # Clear remaining session keys
                for key in ['passport_step_1','passport_step_2','passport_step_3','passport_step_4','passport_step_5','passport_app_id']:
                    if key in request.session:
                        del request.session[key]
                return redirect('passport_dashboard')

            # Navigation
            if 'next' in request.POST:
                next_step = step + 1
                if next_step > 7:
                    next_step = 7
                return redirect('passport_apply_step', step=next_step)

            if 'prev' in request.POST:
                prev_step = step - 1
                if prev_step < 1:
                    prev_step = 1
                return redirect('passport_apply_step', step=prev_step)

            return redirect('passport_apply_step', step=step)

        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, f'passport/apply_step{step}.html', {'form': form, 'step': step, 'total_steps': 7})

    # ---------- GET ----------
    if step == 7 and 'passport_app_id' in request.session:
        app = get_object_or_404(PassportApplication, id=request.session['passport_app_id'], user=request.user)
        form = Step7BiometricForm(initial={'application': app})
        return render(request, 'passport/apply_step7.html', {'form': form, 'step': 7, 'total_steps': 7})

    forms_map = {
        1: Step1PersonalForm,
        2: Step2IdentityForm,
        3: Step3ParentSpouseForm,
        4: Step4AddressForm,
        5: Step5EducationEmploymentTravelForm,
        6: Step6DocumentUploadForm,
        7: Step7BiometricForm,
    }
    FormClass = forms_map.get(step, Step1PersonalForm)
    initial = {}
    if step == 3:
        step1_data = request.session.get('passport_step_1', {})
        if 'marital_status' in step1_data:
            initial['marital_status'] = step1_data['marital_status']
    form = FormClass(initial=initial)
    return render(request, f'passport/apply_step{step}.html', {'form': form, 'step': step, 'total_steps': 7})

# ---------- REMAINING VIEWS (unchanged) ----------
@login_required
def track_application(request, app_id):
    app = get_object_or_404(PassportApplication, id=app_id, user=request.user)
    logs = app.status_logs.all().order_by('-created_at')
    return render(request, 'passport/status.html', {'app': app, 'logs': logs})

@login_required
def receipt(request, app_id):
    app = get_object_or_404(PassportApplication, id=app_id, user=request.user)
    return render(request, 'passport/receipt.html', {'app': app})

@login_required
@user_passes_test(staff_check)
def admin_panel(request):
    applications = PassportApplication.objects.all().order_by('-created_at')
    return render(request, 'passport/admin_panel.html', {'applications': applications})

@login_required
@user_passes_test(staff_check)
def update_status(request, app_id, status):
    app = get_object_or_404(PassportApplication, id=app_id)
    valid_statuses = [choice[0] for choice in PassportApplication.STATUS_CHOICES]
    if status in valid_statuses:
        app.status = status
        app.save()
        StatusLog.objects.create(application=app, status=status, notes=f'Updated by {request.user.username}')
        messages.success(request, f'Application {app.application_id} status updated to {status}')
    else:
        messages.error(request, 'Invalid status')
    return redirect('passport_admin_panel')

@login_required
def view_passport(request, app_id):
    app = get_object_or_404(PassportApplication, id=app_id, user=request.user)
    if app.status not in ['APPROVED', 'PRINTING', 'DISPATCHED', 'DELIVERED']:
        messages.error(request, 'Passport is not yet approved.')
        return redirect('passport_dashboard')
    return render(request, 'passport/passport_view.html', {'app': app})