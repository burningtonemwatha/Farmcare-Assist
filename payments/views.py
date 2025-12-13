# payments/views.py

import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from farmcare.models import Report, Payment
from farmcare.mpesa_service import get_mpesa_service


@login_required
def checkout_view(request, report_id):
    """Payment checkout page"""

    # Report must belong to the logged-in user (farmer)
    report = get_object_or_404(
        Report,
        pk=report_id,
        user=request.user
    )

    # If already paid, stop
    if report.payment_status == 'paid':
        messages.info(request, 'This report has already been paid for.')
        return redirect('farmcare:report_detail', pk=report.pk)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()

        # 🔹 Normalize phone number
        # Remove spaces, +, dashes, etc.
        phone_number = re.sub(r'[^0-9]', '', phone_number)

        # Convert to 2547XXXXXXXX
        if phone_number.startswith('0') and len(phone_number) == 10:
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('7') and len(phone_number) == 9:
            phone_number = '254' + phone_number
        elif phone_number.startswith('254') and len(phone_number) == 12:
            pass
        else:
            messages.error(request, 'Please enter a valid M-Pesa phone number.')
            return render(request, 'payments/checkout.html', {'report': report})

        # Create payment record
        payment = Payment.objects.create(
            report=report,
            user=request.user,
            amount=report.amount,
            phone_number=phone_number,
            transaction_status='initiated'
        )

        # Initiate STK Push
        mpesa_service = get_mpesa_service(use_sandbox=True)
        response = mpesa_service.initiate_stk_push(
            phone_number=phone_number,
            amount=report.amount,
            account_reference=f"REPORT-{report.pk}",
            description=f"Payment for {report.title}",
            request=request
        )

        # If M-Pesa failed
        if 'error' in response:
            payment.transaction_status = 'failed'
            payment.mpesa_result_description = response.get('error')
            payment.save()

            messages.error(request, f"Error initiating payment: {response['error']}")
            return render(request, 'payments/checkout.html', {'report': report})

        # Save M-Pesa IDs
        payment.mpesa_checkout_request_id = response.get('CheckoutRequestID')
        payment.mpesa_merchant_request_id = response.get('MerchantRequestID')
        payment.transaction_status = 'pending'
        payment.save()

        # Update report status
        report.payment_status = 'pending'
        report.save()

        messages.success(
            request,
            f"STK push sent to {phone_number}. Enter your M-Pesa PIN."
        )

        return redirect('payments:status', payment_id=payment.pk)

    return render(request, 'payments/checkout.html', {'report': report})


@login_required
def payment_status_view(request, payment_id):
    """Payment status page"""

    payment = get_object_or_404(
        Payment,
        pk=payment_id,
        report__user=request.user
    )

    return render(request, 'payments/status.html', {
        'payment': payment,
        'report': payment.report
    })


@login_required
@require_POST
def check_payment_status_ajax(request, payment_id):
    """AJAX endpoint to check payment status"""

    payment = get_object_or_404(
        Payment,
        pk=payment_id,
        report__user=request.user
    )

    report = payment.report

    if payment.mpesa_checkout_request_id:
        mpesa_service = get_mpesa_service(use_sandbox=True)
        status_response = mpesa_service.check_transaction_status(
            payment.mpesa_checkout_request_id
        )

        if 'error' not in status_response:
            if status_response.get('ResultCode') == '0':
                payment.transaction_status = 'success'
                payment.mpesa_result_code = '0'
                payment.mpesa_result_description = status_response.get('ResultDesc')
                payment.save()

                report.payment_status = 'paid'
                report.save()

    return JsonResponse({
        'payment_status': payment.transaction_status,
        'report_payment_status': report.payment_status,
        'result_code': payment.mpesa_result_code,
        'result_description': payment.mpesa_result_description,
    })
