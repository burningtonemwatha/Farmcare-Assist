# M-Pesa Payment Integration Guide

## Overview
The AgriWatch platform now supports M-Pesa payments through Safaricom's Daraja API. Farmers must pay a consultation fee (default 500 KES) before experts review their reports.

## Architecture

### Models
1. **Report** - Enhanced with payment fields:
   - `payment_status`: unpaid, pending, paid, failed
   - `amount`: Payment amount in KES (default 500.00)

2. **Payment** - New model for tracking transactions:
   - Stores user, report, amount, phone number
   - Tracks M-Pesa request IDs and receipt numbers
   - Records transaction status (initiated, pending, success, failed, cancelled)

### Services
- `farmcare/mpesa_service.py` - M-Pesa integration service
  - `get_access_token()` - Gets OAuth token from Daraja API
  - `initiate_stk_push()` - Sends STK prompt to customer phone
  - `check_transaction_status()` - Queries transaction status
  - `process_callback()` - Handles M-Pesa callback data

### Views
1. `payment_checkout_view` - Display payment form and initiate STK push
2. `payment_status_view` - Show payment status with auto-refresh
3. `check_payment_status_ajax` - AJAX endpoint to poll transaction status
4. `mpesa_callback_view` - Webhook to receive M-Pesa callbacks (CSRF exempt)

### Templates
- `payment_checkout.html` - Payment form with phone number input
- `payment_status.html` - Status checker with auto-refresh JavaScript

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure M-Pesa Credentials
Create a `.env` file with M-Pesa settings:

```env
# M-Pesa (Daraja) Credentials
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-lipa-na-mpesa-online-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/farmcare/payment/callback/
```

**To get these credentials:**
1. Register at https://developer.safaricom.co.ke/
2. Create a new app
3. Copy Consumer Key and Consumer Secret
4. Go to Lipa Na M-Pesa Online section and generate your passkey

### 3. Run Migrations
```bash
python manage.py migrate
```

## Payment Flow

### User (Farmer) Side
1. Creates a farm issue report
2. Views report detail page
3. Clicks "Pay with M-Pesa" button
4. Enters M-Pesa phone number
5. Receives STK push on phone
6. Enters M-Pesa PIN to complete payment
7. Page auto-refreshes to show payment confirmed

### Expert Side
1. Accesses Expert Dashboard
2. Sees "Payment" column showing:
   - ✓ **Paid** (green) - Payment received
   - ⏳ **Pending** (yellow) - Awaiting confirmation
   - ✗ **Failed** (red) - Payment failed
   - ⊘ **Unpaid** (gray) - Not paid
3. Can click "View & Update" to see payment details
4. Report shows payment status badge in detail view

## Database Schema

### Report Model Updates
```python
payment_status = CharField(
    max_length=20, 
    choices=[('unpaid', 'Unpaid'), ('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
    default='unpaid'
)
amount = DecimalField(max_digits=10, decimal_places=2, default=500.00)
```

### Payment Model
```python
class Payment(models.Model):
    report = ForeignKey(Report)
    user = ForeignKey(User)
    amount = DecimalField()
    phone_number = CharField()
    payment_method = CharField(default='mpesa')
    transaction_status = CharField(choices=[...])
    
    # M-Pesa specific fields
    mpesa_checkout_request_id = CharField()
    mpesa_merchant_request_id = CharField()
    mpesa_result_code = CharField()
    mpesa_result_description = TextField()
    mpesa_receipt_number = CharField()
    
    created_at = DateTimeField()
    updated_at = DateTimeField()
```

## Testing

### Using Sandbox
The system uses Safaricom's **sandbox environment** by default for testing.

**Test M-Pesa Numbers (Sandbox):**
- `254708374149` - Always succeeds
- `254707202626` - Check results, will return error
- `254708374149` - Success (default)

### Testing Flow
1. Register as a farmer
2. Create a farm issue report
3. Click "Pay with M-Pesa"
4. Enter test phone number: `0708374149` or `254708374149`
5. Payment is simulated (no actual money deducted)
6. Status updates after callback from M-Pesa sandbox

### Switch to Production
To use live M-Pesa:
1. Update `farmcare/mpesa_service.py` line 26:
   ```python
   def __init__(self, use_sandbox=False):  # Changed from True
   ```
2. Ensure `MPESA_CALLBACK_URL` points to your production domain
3. Use real M-Pesa credentials from production app

## API Endpoints

### Payment Routes
- `POST /farmcare/report/<id>/payment/checkout/` - Initiate payment
- `GET /farmcare/report/<id>/payment/status/` - Check status
- `POST /farmcare/payment/check-status/<id>/` - AJAX status check
- `POST /farmcare/payment/callback/` - M-Pesa callback webhook (public)

## Security Notes

1. **CSRF Exemption**: The callback endpoint must be exempt from CSRF to accept M-Pesa webhooks
2. **Phone Validation**: Accepts both `0712345678` and `254712345678` formats
3. **Amount Validation**: Server validates amount matches report amount
4. **Payment Verification**: Callback updates payment status atomically

## Troubleshooting

### "Failed to get access token"
- Verify M-Pesa credentials in `.env`
- Check internet connection
- Ensure credentials are from the correct sandbox/production environment

### "Invalid phone number"
- Ensure phone starts with 254 (country code)
- Or starts with 0 (for Kenyan numbers)
- Format: `254712345678` or `0712345678`

### Payment not confirming
- M-Pesa callback may be delayed (usually 2-5 seconds)
- Status page auto-refreshes for up to 60 seconds
- Manual page refresh will check again
- Check `Payment` model in Django admin for transaction status

### STK not appearing on phone
- Phone number may not be registered with M-Pesa
- May be network issue (try again in a few seconds)
- Use test number `254708374149` for sandbox testing

## Admin Interface

Access Django admin at `/admin/`:
- **Payments** section shows all transactions
- Filter by status, payment method, date
- View M-Pesa receipt numbers and result codes
- Update payment status manually if needed

## Next Steps (Optional)

1. **SMS Notifications**: Add SMS alerts when payment received
2. **Invoice Generation**: Create PDF invoices for farmers
3. **Subscription Plans**: Offer monthly or annual consultation packages
4. **Analytics**: Track payment metrics and expert earnings
5. **Refunds**: Implement refund mechanism for failed services
6. **Multiple Payment Methods**: Add Stripe, PayPal support

## Support

For M-Pesa API documentation: https://developer.safaricom.co.ke/

