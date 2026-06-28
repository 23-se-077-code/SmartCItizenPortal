from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Complaint
from .forms import ComplaintForm

@login_required
def complaint_list(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'complaints/list.html', {'complaints': complaints})

@login_required
def add_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            # Auto-fill email from user if not provided
            if not complaint.email:
                complaint.email = request.user.email
            complaint.save()
            messages.success(request, f"""
                ✅ Your complaint has been received! 
                Reference ID: {complaint.reference_number}. 
                We will review it shortly and contact you via {complaint.phone or 'email'} if needed. 
                Thank you for helping us improve.
            """)
            return redirect('complaints')
    else:
        # Pre-fill email from logged-in user
        initial_data = {'email': request.user.email}
        form = ComplaintForm(initial=initial_data)
    
    return render(request, 'complaints/add.html', {'form': form})