import hashlib
import requests
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import BillCategory, ChallanCategory, Bill, Challan, PaymentTransaction
from .forms import BillPaymentForm, ChallanPaymentForm

# ---------- HELPER: Simulation Fallback ----------
def simulate_payment(request, item, item_type):
    if item_type == 'bill':
        item.status = 'paid'
        item.save()
        trans = PaymentTransaction.objects.create(
            user=request.user,
            payment_type='bill',
            bill=item,
            amount=item.amount,
            transaction_id=f"SIM{datetime.now().strftime('%Y%m%d%H%M%S')}",
            gateway_name='simulation',
            is_successful=True
        )
        messages.success(request, f"Bill of Rs. {item.amount} paid successfully (simulated).")
        return redirect('challan:payment_success', transaction_id=trans.transaction_id)
    elif item_type == 'challan':
        item.status = 'paid'
        item.save()
        trans = PaymentTransaction.objects.create(
            user=request.user,
            payment_type='challan',
            challan=item,
            amount=item.amount,
            transaction_id=f"SIM{datetime.now().strftime('%Y%m%d%H%M%S')}",
            gateway_name='simulation',
            is_successful=True
        )
        messages.success(request, f"Challan of Rs. {item.amount} paid successfully (simulated).")
        return redirect('challan:payment_success', transaction_id=trans.transaction_id)
    else:
        messages.error(request, "Invalid payment type.")
        return redirect('challan:dashboard')

# ---------- DASHBOARD ----------
@login_required
def dashboard(request):
    bill_categories = BillCategory.objects.all()
    challan_categories = ChallanCategory.objects.all()
    bills = Bill.objects.filter(status='unpaid').order_by('due_date')[:5]
    challans = Challan.objects.filter(status='unpaid').order_by('due_date')[:5]
    recent_payments = PaymentTransaction.objects.filter(user=request.user).order_by('-paid_at')[:5]
    total_paid = PaymentTransaction.objects.filter(user=request.user, is_successful=True).aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'challan/dashboard.html', {
        'bills': bills,
        'challans': challans,
        'recent_payments': recent_payments,
        'total_paid': total_paid,
        'bill_categories': bill_categories,
        'challan_categories': challan_categories,
    })

# ---------- LISTS ----------
@login_required
def bill_list(request):
    categories = BillCategory.objects.all()
    selected_category = request.GET.get('category')
    if selected_category:
        bills = Bill.objects.filter(category__slug=selected_category, status='unpaid')
    else:
        bills = Bill.objects.filter(status='unpaid')
    return render(request, 'challan/bill_list.html', {
        'bills': bills,
        'categories': categories,
        'selected_category': selected_category,
    })

@login_required
def challan_list(request):
    categories = ChallanCategory.objects.all()
    selected_category = request.GET.get('category')
    if selected_category:
        challans = Challan.objects.filter(category__slug=selected_category, status='unpaid')
    else:
        challans = Challan.objects.filter(status='unpaid')
    return render(request, 'challan/challan_list.html', {
        'challans': challans,
        'categories': categories,
        'selected_category': selected_category,
    })

# ---------- BILL PAYMENT STEPS ----------
@login_required
def pay_bill_step1(request):
    categories = BillCategory.objects.all()
    return render(request, 'challan/pay_bill_step1.html', {'categories': categories})

@login_required
def pay_bill_step2(request, category_slug):
    category = get_object_or_404(BillCategory, slug=category_slug)
    if request.method == 'POST':
        form = BillPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.category = category
            bill.status = 'unpaid'
            bill.save()
            return redirect('challan:pay_bill_confirm', bill_id=bill.id)
    else:
        initial = {
            'consumer_number': 'CNS-001',
            'consumer_name': request.user.username,
            'amount': 1500,
            'due_date': '2025-12-31',
        }
        form = BillPaymentForm(initial=initial)
    return render(request, 'challan/pay_bill_step2.html', {'form': form, 'category': category})

@login_required
def pay_bill_confirm(request, bill_id):
    try:
        bill = Bill.objects.get(id=bill_id, status='unpaid')
    except Bill.DoesNotExist:
        messages.error(request, "Bill not found or already paid.")
        return redirect('challan:bill_list')

    if request.method == 'POST':
        PaymentTransaction.objects.create(
            user=request.user,
            payment_type='bill',
            bill=bill,
            amount=bill.amount,
            is_successful=True
        )
        bill.status = 'paid'
        bill.save()
        messages.success(request, f"Bill of Rs. {bill.amount} paid successfully!")
        return redirect('challan:payment_success', transaction_id=PaymentTransaction.objects.latest('id').transaction_id)
    return render(request, 'challan/pay_bill_confirm.html', {'bill': bill})

# ---------- CHALLAN PAYMENT STEPS ----------
@login_required
def pay_challan_step1(request):
    categories = ChallanCategory.objects.all()
    return render(request, 'challan/pay_challan_step1.html', {'categories': categories})

@login_required
def pay_challan_step2(request, category_slug):
    category = get_object_or_404(ChallanCategory, slug=category_slug)
    if request.method == 'POST':
        form = ChallanPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            challan = form.save(commit=False)
            challan.category = category
            challan.status = 'unpaid'
            challan.save()
            return redirect('challan:pay_challan_confirm', challan_id=challan.id)
    else:
        initial = {
            'challan_number': 'CH-001',
            'citizen_name': request.user.username,
            'cnic': '42101-1234567-1',
            'amount': 500,
            'due_date': '2025-12-31',
        }
        form = ChallanPaymentForm(initial=initial)
    return render(request, 'challan/pay_challan_step2.html', {'form': form, 'category': category})

@login_required
def pay_challan_confirm(request, challan_id):
    try:
        challan = Challan.objects.get(id=challan_id, status='unpaid')
    except Challan.DoesNotExist:
        messages.error(request, "Challan not found or already paid.")
        return redirect('challan:challan_list')

    if request.method == 'POST':
        PaymentTransaction.objects.create(
            user=request.user,
            payment_type='challan',
            challan=challan,
            amount=challan.amount,
            is_successful=True
        )
        challan.status = 'paid'
        challan.save()
        messages.success(request, f"Challan of Rs. {challan.amount} paid successfully!")
        return redirect('challan:payment_success', transaction_id=PaymentTransaction.objects.latest('id').transaction_id)
    return render(request, 'challan/pay_challan_confirm.html', {'challan': challan})

# ---------- APPLICATION FEE PAYMENT ----------
@login_required
def pay_application_fee(request, app_type, app_id):
    if app_type == 'cnic':
        from cnic.models import CNICApplication
        app = get_object_or_404(CNICApplication, id=app_id, user=request.user)
        fee = app.fee
        reference = app.application_id
    elif app_type == 'passport':
        from passport.models import PassportApplication
        app = get_object_or_404(PassportApplication, id=app_id, user=request.user)
        fee = app.fee
        reference = app.application_id
    else:
        messages.error(request, "Invalid application type.")
        return redirect('challan:dashboard')

    if request.method == 'POST':
        transaction = PaymentTransaction.objects.create(
            user=request.user,
            payment_type='application',
            amount=fee,
            is_successful=True,
            app_type=app_type,
            app_id=app.id,
            reference_number=reference,
            gateway_name='simulation',
            transaction_id=f"APP{datetime.now().strftime('%Y%m%d%H%M%S')}{app.id}"
        )
        app.status = 'SUBMITTED'
        app.payment_status = 'PAID'
        app.payment_transaction = transaction
        app.save()
        messages.success(request, f"Payment of PKR {fee} successful! Application submitted.")
        return redirect('challan:payment_success', transaction_id=transaction.transaction_id)

    return render(request, 'challan/pay_application_fee.html', {
        'app': app,
        'fee': fee,
        'reference': reference,
        'app_type': app_type,
    })

# ---------- JAZZCASH ----------
@login_required
def jazzcash_redirect(request, bill_id=None, challan_id=None):
    if bill_id:
        try:
            item = Bill.objects.get(id=bill_id, status='unpaid')
        except Bill.DoesNotExist:
            messages.error(request, "Bill not found or already paid.")
            return redirect('challan:bill_list')
        item_type = 'bill'
        description = f"Bill Payment: {item.category.name} for {item.consumer_name}"
        ref_field = str(item.id)
    elif challan_id:
        try:
            item = Challan.objects.get(id=challan_id, status='unpaid')
        except Challan.DoesNotExist:
            messages.error(request, "Challan not found or already paid.")
            return redirect('challan:challan_list')
        item_type = 'challan'
        description = f"Challan Payment: {item.category.name} for {item.citizen_name}"
        ref_field = str(item.id)
    else:
        messages.error(request, "Invalid request")
        return redirect('challan:dashboard')

    if not getattr(settings, 'JAZZCASH_MERCHANT_ID', None):
        messages.warning(request, "JazzCash credentials not set. Using simulation.")
        return simulate_payment(request, item, item_type)

    merchant_id = settings.JAZZCASH_MERCHANT_ID
    password = settings.JAZZCASH_PASSWORD
    integrity_salt = settings.JAZZCASH_INTEGRITY_SALT
    return_url = settings.JAZZCASH_RETURN_URL

    amount = int(item.amount * 100)
    txn_ref_no = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{item.id}"
    txn_date_time = datetime.now().strftime('%Y%m%d%H%M%S')

    post_data = {
        'pp_Version': '1.1',
        'pp_TxnType': 'MPAY',
        'pp_MerchantID': merchant_id,
        'pp_Password': password,
        'pp_TxnRefNo': txn_ref_no,
        'pp_Amount': str(amount),
        'pp_TxnCurrency': 'PKR',
        'pp_TxnDateTime': txn_date_time,
        'pp_BillReference': ref_field,
        'pp_Description': description,
        'pp_TxnExpiryDateTime': '',
        'pp_ReturnURL': return_url,
        'pp_SecureHash': '',
    }

    hash_string = f"{integrity_salt}&{post_data['pp_Amount']}&{post_data['pp_BillReference']}&{post_data['pp_Description']}&{post_data['pp_MerchantID']}&{post_data['pp_Password']}&{post_data['pp_ReturnURL']}&{post_data['pp_TxnCurrency']}&{post_data['pp_TxnDateTime']}&{post_data['pp_TxnRefNo']}&{post_data['pp_Version']}"
    post_data['pp_SecureHash'] = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

    jazzcash_url = getattr(settings, 'JAZZCASH_SANDBOX_URL', 'https://sandbox.jazzcash.com.pk/ApplicationAPI/API/Payment/DoPayment')

    request.session['jazzcash_item_type'] = item_type
    request.session['jazzcash_item_id'] = item.id

    try:
        resp = requests.post(jazzcash_url, data=post_data, timeout=10)
        if resp.status_code == 200:
            return render(request, 'challan/jazzcash_redirect.html', {
                'post_data': post_data,
                'jazzcash_url': jazzcash_url,
            })
        else:
            messages.warning(request, "JazzCash API error. Using simulation.")
            return simulate_payment(request, item, item_type)
    except Exception as e:
        messages.warning(request, f"JazzCash connection error: {str(e)}. Using simulation.")
        return simulate_payment(request, item, item_type)

@login_required
def jazzcash_return(request):
    response = request.POST
    if not response:
        messages.error(request, "No response from JazzCash.")
        return redirect('challan:dashboard')

    if response.get('pp_ResponseCode') == '000':
        item_type = request.session.get('jazzcash_item_type')
        item_id = request.session.get('jazzcash_item_id')
        if item_type == 'bill':
            try:
                bill = Bill.objects.get(id=item_id, status='unpaid')
                bill.status = 'paid'
                bill.save()
            except Bill.DoesNotExist:
                messages.error(request, "Bill not found.")
                return redirect('challan:dashboard')
            PaymentTransaction.objects.create(
                user=request.user,
                payment_type='bill',
                bill=bill,
                amount=bill.amount,
                transaction_id=response.get('pp_TxnRefNo', 'JC-001'),
                gateway_transaction_id=response.get('pp_TxnRefNo', ''),
                gateway_name='jazzcash',
                is_successful=True
            )
            messages.success(request, "Bill paid successfully via JazzCash!")
        elif item_type == 'challan':
            try:
                challan = Challan.objects.get(id=item_id, status='unpaid')
                challan.status = 'paid'
                challan.save()
            except Challan.DoesNotExist:
                messages.error(request, "Challan not found.")
                return redirect('challan:dashboard')
            PaymentTransaction.objects.create(
                user=request.user,
                payment_type='challan',
                challan=challan,
                amount=challan.amount,
                transaction_id=response.get('pp_TxnRefNo', 'JC-001'),
                gateway_transaction_id=response.get('pp_TxnRefNo', ''),
                gateway_name='jazzcash',
                is_successful=True
            )
            messages.success(request, "Challan paid successfully via JazzCash!")
        return redirect('challan:payment_success', transaction_id=response.get('pp_TxnRefNo', 'JC-001'))
    else:
        messages.error(request, f"Payment failed: {response.get('pp_ResponseMessage', 'Unknown error')}")
        return redirect('challan:dashboard')

# ---------- EASYPAISA ----------
@login_required
def easypaisa_redirect(request, bill_id=None, challan_id=None):
    if bill_id:
        try:
            item = Bill.objects.get(id=bill_id, status='unpaid')
        except Bill.DoesNotExist:
            messages.error(request, "Bill not found or already paid.")
            return redirect('challan:bill_list')
        item_type = 'bill'
    elif challan_id:
        try:
            item = Challan.objects.get(id=challan_id, status='unpaid')
        except Challan.DoesNotExist:
            messages.error(request, "Challan not found or already paid.")
            return redirect('challan:challan_list')
        item_type = 'challan'
    else:
        messages.error(request, "Invalid request")
        return redirect('challan:dashboard')

    if not getattr(settings, 'EASYPAISA_MERCHANT_ID', None):
        messages.warning(request, "EasyPaisa credentials not set. Using simulation.")
        return simulate_payment(request, item, item_type)

    amount = int(item.amount)
    order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{item.id}"

    payload = {
        'merchantId': settings.EASYPAISA_MERCHANT_ID,
        'password': settings.EASYPAISA_PASSWORD,
        'orderId': order_id,
        'amount': str(amount),
        'returnUrl': settings.EASYPAISA_RETURN_URL,
        'transactionType': 'SALE',
        'currencyCode': 'PKR',
        'description': f"{item_type.capitalize()} Payment",
    }

    request.session['easypaisa_item_type'] = item_type
    request.session['easypaisa_item_id'] = item.id

    url = getattr(settings, 'EASYPAISA_SANDBOX_URL', 'https://easypaystg.easypaisa.com.pk/easypay-service/rest/v4/...')
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success' and data.get('redirectUrl'):
                return redirect(data['redirectUrl'])
            else:
                messages.warning(request, f"EasyPaisa error: {data.get('message', 'Unknown')}. Using simulation.")
                return simulate_payment(request, item, item_type)
        else:
            messages.warning(request, "EasyPaisa service unavailable. Using simulation.")
            return simulate_payment(request, item, item_type)
    except Exception as e:
        messages.warning(request, f"EasyPaisa error: {str(e)}. Using simulation.")
        return simulate_payment(request, item, item_type)

@login_required
def easypaisa_return(request):
    response = request.GET or request.POST
    if response.get('status') == 'success' or response.get('isSuccess') == 'true':
        item_type = request.session.get('easypaisa_item_type')
        item_id = request.session.get('easypaisa_item_id')
        if item_type == 'bill':
            try:
                bill = Bill.objects.get(id=item_id, status='unpaid')
                bill.status = 'paid'
                bill.save()
            except Bill.DoesNotExist:
                messages.error(request, "Bill not found.")
                return redirect('challan:dashboard')
            PaymentTransaction.objects.create(
                user=request.user,
                payment_type='bill',
                bill=bill,
                amount=bill.amount,
                transaction_id=response.get('orderId', 'EP-001'),
                gateway_transaction_id=response.get('transactionId', ''),
                gateway_name='easypaisa',
                is_successful=True
            )
            messages.success(request, "Bill paid via EasyPaisa!")
        elif item_type == 'challan':
            try:
                challan = Challan.objects.get(id=item_id, status='unpaid')
                challan.status = 'paid'
                challan.save()
            except Challan.DoesNotExist:
                messages.error(request, "Challan not found.")
                return redirect('challan:dashboard')
            PaymentTransaction.objects.create(
                user=request.user,
                payment_type='challan',
                challan=challan,
                amount=challan.amount,
                transaction_id=response.get('orderId', 'EP-001'),
                gateway_transaction_id=response.get('transactionId', ''),
                gateway_name='easypaisa',
                is_successful=True
            )
            messages.success(request, "Challan paid via EasyPaisa!")
        return redirect('challan:payment_success', transaction_id=response.get('orderId', 'EP-001'))
    else:
        messages.error(request, f"Payment failed: {response.get('message', 'Unknown error')}")
        return redirect('challan:dashboard')

# ---------- SUCCESS & HISTORY ----------
@login_required
def payment_success(request, transaction_id):
    try:
        transaction = PaymentTransaction.objects.get(transaction_id=transaction_id, user=request.user)
    except PaymentTransaction.DoesNotExist:
        messages.error(request, "Transaction not found.")
        return redirect('challan:dashboard')
    return render(request, 'challan/payment_success.html', {'transaction': transaction})

@login_required
def payment_history(request):
    payments = PaymentTransaction.objects.filter(user=request.user).order_by('-paid_at')
    return render(request, 'challan/history.html', {'payments': payments})