import base64
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db import transaction
from .forms import BiometricVerificationForm, ProvinceForm, AssemblyForm, ConstituencyForm, CandidateForm
from .models import Candidate, Vote, AssemblyType, UserProfile, Constituency, Province

# ---------- HELPER ----------
def get_profile(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile

# ---------- DASHBOARD ----------
@login_required
def dashboard(request):
    profile = get_profile(request.user)
    has_voted_na = Vote.objects.filter(user=request.user, constituency__assembly__code='NA').exists()
    has_voted_pa = Vote.objects.filter(
        user=request.user,
        constituency__assembly__code__in=['PP','PS','PK','PB','PG','PKS']
    ).exists()
    return render(request, "voting/dashboard.html", {
        "profile": profile,
        "has_voted_na": has_voted_na,
        "has_voted_pa": has_voted_pa,
    })

# ---------- VERIFICATION ----------
@login_required
def voting_verification(request):
    profile = get_profile(request.user)
    if profile.is_verified:
        return redirect('voting_wizard_step', step=1)

    if request.method == "POST":
        form = BiometricVerificationForm(request.POST, request.FILES)
        dob_input = request.POST.get("date_of_birth")

        if not dob_input:
            messages.error(request, "Please enter your Date of Birth.")
            return render(request, "voting/verify_identity.html", {"form": form, "profile": profile})

        try:
            parsed_dob = datetime.strptime(dob_input, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            return render(request, "voting/verify_identity.html", {"form": form, "profile": profile})

        if not profile.date_of_birth:
            profile.date_of_birth = parsed_dob
        elif profile.date_of_birth != parsed_dob:
            messages.error(request, "Date of Birth does not match our records.")
            return render(request, "voting/verify_identity.html", {"form": form, "profile": profile})

        image_data = request.POST.get("live_selfie_data")
        if not image_data or not image_data.startswith("data:image"):
            messages.error(request, "Please capture a live selfie using the webcam.")
            return render(request, "voting/verify_identity.html", {"form": form, "profile": profile})

        try:
            fmt, imgstr = image_data.split(';base64,')
            ext = fmt.split('/')[-1]
            selfie_file = ContentFile(base64.b64decode(imgstr), name=f"selfie_{request.user.id}.{ext}")
            profile.selfie = selfie_file
        except Exception as e:
            messages.error(request, f"Failed to decode selfie image: {str(e)}")
            return render(request, "voting/verify_identity.html", {"form": form, "profile": profile})

        if 'cnic_photo' not in request.FILES:
            messages.error(request, "Please upload a photo of your CNIC.")
            return render(request, "voting/verify_identity.html", {"form": form, "profile": profile})

        profile.cnic_photo = request.FILES['cnic_photo']
        profile.is_verified = True
        profile.save()
        messages.success(request, "✅ Verification successful! You can now vote.")
        return redirect('voting_wizard_step', step=1)

    else:
        form = BiometricVerificationForm()

    return render(request, "voting/verify_identity.html", {"form": form, "profile": profile})

# ---------- WIZARD ----------
@login_required
def vote_wizard(request, step):
    profile = get_profile(request.user)

    if not profile.is_verified:
        messages.error(request, "You must verify your identity first.")
        return redirect('verify_identity')

    # Step 1: Province
    if step == 1:
        if request.method == "POST":
            form = ProvinceForm(request.POST)
            if form.is_valid():
                request.session["vote_province_id"] = form.cleaned_data["province"].id
                return redirect('voting_wizard_step', step=2)
        else:
            form = ProvinceForm()
        return render(request, "voting/step1_province.html", {"form": form, "profile": profile})

    # Step 2: Assembly – show all, but only enabled for assigned ones
    elif step == 2:
        province_id = request.session.get("vote_province_id")
        if not province_id:
            return redirect('voting_wizard_step', step=1)

        province = get_object_or_404(Province, id=province_id)
        assemblies = AssemblyType.objects.filter(province=province)

        assembly_list = []
        for assembly in assemblies:
            assigned_constituency = None
            if assembly.code == 'NA':
                assigned_constituency = profile.assigned_na_constituency
            else:
                assigned_constituency = profile.assigned_pa_constituency

            is_assigned = assigned_constituency is not None and assigned_constituency.assembly == assembly

            has_voted = Vote.objects.filter(
                user=request.user,
                constituency__assembly=assembly
            ).exists() if is_assigned else True

            assembly_list.append({
                'assembly': assembly,
                'assigned': is_assigned,
                'has_voted': has_voted,
                'can_vote': is_assigned and not has_voted,
                'assigned_constituency': assigned_constituency,
            })

        if request.method == "POST":
            assembly_id = request.POST.get("assembly_id")
            if not assembly_id:
                messages.error(request, "Please select an assembly.")
                return redirect('voting_wizard_step', step=2)

            assembly = get_object_or_404(AssemblyType, id=assembly_id)
            if assembly.code == 'NA':
                assigned = profile.assigned_na_constituency
            else:
                assigned = profile.assigned_pa_constituency

            if not assigned or assigned.assembly != assembly:
                messages.error(request, f"You are not assigned to {assembly.name}. Please visit your desired constituency.")
                return redirect('voting_wizard_step', step=2)

            request.session["vote_assembly_id"] = assembly.id
            return redirect('voting_wizard_step', step=3)

        return render(request, "voting/step2_assembly.html", {
            "province": province,
            "assemblies": assembly_list,
            "profile": profile,
        })

    # Step 3: Constituency – show all, but only assigned one is clickable
    elif step == 3:
        assembly_id = request.session.get("vote_assembly_id")
        if not assembly_id:
            return redirect('voting_wizard_step', step=2)

        assembly = get_object_or_404(AssemblyType, id=assembly_id)
        if assembly.code == 'NA':
            allowed = profile.assigned_na_constituency
        else:
            allowed = profile.assigned_pa_constituency

        all_constituencies = Constituency.objects.filter(assembly=assembly).order_by('code')

        constituency_list = []
        for const in all_constituencies:
            is_assigned = (allowed and const.id == allowed.id)
            has_voted = Vote.objects.filter(user=request.user, constituency=const).exists()
            constituency_list.append({
                'constituency': const,
                'assigned': is_assigned,
                'has_voted': has_voted,
                'can_select': is_assigned and not has_voted,
            })

        if request.method == "POST":
            constituency_id = request.POST.get("constituency_id")
            if not constituency_id:
                messages.error(request, "Please select your constituency.")
                return render(request, "voting/step3_constituency.html", {
                    "constituencies": constituency_list,
                    "assembly": assembly,
                    "allowed": allowed,
                })
            selected = get_object_or_404(Constituency, id=constituency_id)
            if not allowed or selected != allowed:
                messages.error(request, f"You can only vote in {allowed.code}.")
                return redirect('voting_wizard_step', step=3)
            request.session["vote_constituency_id"] = selected.id
            return redirect('voting_wizard_step', step=4)

        return render(request, "voting/step3_constituency.html", {
            "constituencies": constituency_list,
            "assembly": assembly,
            "allowed": allowed,
        })

    # Step 4: Cast Vote
    elif step == 4:
        constituency_id = request.session.get("vote_constituency_id")
        if not constituency_id:
            return redirect('voting_wizard_step', step=3)

        if request.method == "POST":
            form = CandidateForm(request.POST, constituency_id=constituency_id)
            if form.is_valid():
                candidate = form.cleaned_data["candidate"]
                if Vote.objects.filter(user=request.user, constituency=candidate.constituency).exists():
                    messages.error(request, "You already voted in this constituency.")
                    return redirect('voting_dashboard')

                with transaction.atomic():
                    # Create the vote
                    Vote.objects.create(
                        user=request.user,
                        constituency=candidate.constituency,
                        candidate=candidate
                    )
                    # Increment the vote count
                    candidate.votes += 1
                    candidate.save()

                # Clear session
                for key in ["vote_province_id", "vote_assembly_id", "vote_constituency_id"]:
                    if key in request.session:
                        del request.session[key]

                messages.success(request, f"✅ Vote for {candidate.name} recorded!")
                return redirect('voting_results')
        else:
            form = CandidateForm(constituency_id=constituency_id)
        return render(request, "voting/step4_vote.html", {"form": form, "profile": profile})

    return redirect('voting_dashboard')

# ---------- RESULTS ----------
@login_required
def results(request):
    data = []
    for c in Constituency.objects.all().order_by('code'):
        candidates = c.candidates.all().order_by('-votes')
        # Only determine winner if any candidate has votes > 0
        winner = None
        for cand in candidates:
            if cand.votes > 0:
                winner = cand
                break
        data.append({
            "constituency": c,
            "candidates": candidates,
            "winner": winner,
            "has_votes": any(cand.votes > 0 for cand in candidates),
        })
    return render(request, "voting/results.html", {"results": data})

# ---------- UPDATE PROFILE ----------
@login_required
def update_profile(request):
    profile = get_profile(request.user)
    if request.method == "POST":
        from .forms import UserProfileForm
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('voting_dashboard')
    else:
        from .forms import UserProfileForm
        form = UserProfileForm(instance=profile)
    return render(request, "voting/update_profile.html", {"form": form, "profile": profile})