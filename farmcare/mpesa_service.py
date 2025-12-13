"""
M-Pesa payment integration service using python-daraja
"""
import os
import logging
from datetime import datetime
from decimal import Decimal
import requests
from decouple import config
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

logger = logging.getLogger(__name__)


class MpesaService:
    """Service for handling M-Pesa STK push and callback processing"""
    
    # M-Pesa API endpoints
    SANDBOX_BASE_URL = "https://sandbox.safaricom.co.ke"
    PRODUCTION_BASE_URL = "https://api.safaricom.co.ke"
    
    def __init__(self, use_sandbox=True):
        self.use_sandbox = use_sandbox
        self.base_url = self.SANDBOX_BASE_URL if use_sandbox else self.PRODUCTION_BASE_URL
        
        # M-Pesa credentials from environment
        # Support both MPESA_* names and legacy names (CONSUMER_KEY, CONSUMER_SECRET, SHORTCODE, PASSKEY)
        def _get(var_candidates, default=''):
            for name in var_candidates:
                try:
                    val = config(name, default=None)
                except Exception:
                    val = None
                if val is not None and val != '':
                    # strip whitespace and surrounding quotes if present
                    return val.strip().strip('"\'"')
            return default

        self.consumer_key = _get(['MPESA_CONSUMER_KEY', 'CONSUMER_KEY'], '')
        self.consumer_secret = _get(['MPESA_CONSUMER_SECRET', 'CONSUMER_SECRET'], '')
        self.business_shortcode = _get(['MPESA_SHORTCODE', 'SHORTCODE'], '174379')
        self.passkey = _get(['MPESA_PASSKEY', 'PASSKEY'], '')
        self.callback_url = _get(['MPESA_CALLBACK_URL', 'CALLBACK_URL'], '')

        # Allow optional BASE_URL override (useful in some setups)
        base_override = _get(['MPESA_BASE_URL', 'BASE_URL'], '')
        if base_override:
            # strip surrounding quotes if any and use as-is
            self.base_url = base_override
    
    def get_access_token(self):
        """Get M-Pesa access token"""
        try:
            endpoint = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            auth = (self.consumer_key, self.consumer_secret)
            
            response = requests.get(endpoint, auth=auth, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('access_token')
        except Exception as e:
            logger.error(f"Error getting M-Pesa access token: {str(e)}")
            return None
    
    def initiate_stk_push(self, phone_number, amount, account_reference, description, request=None):
        """
        Initiate STK push for M-Pesa payment
        
        Args:
            phone_number: Customer's phone number (format: 254712345678)
            amount: Payment amount in KES
            account_reference: Reference (e.g., report_id)
            description: Description of payment
            request: Django request object for callback URL
        
        Returns:
            dict: Response from M-Pesa API
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'error': 'Failed to get access token'}
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Build password: shortcode + passkey + timestamp (base64 encoded)
            password_str = self.business_shortcode + self.passkey + timestamp
            import base64
            password = base64.b64encode(password_str.encode()).decode()
            
            # Build callback URL if request provided
            callback_url = self.callback_url
            if request:
                callback_url = request.build_absolute_uri(reverse('farmcare:mpesa_callback'))
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(float(amount)),
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url,
                "AccountReference": str(account_reference),
                "TransactionDesc": description[:80],  # Limit to 80 chars
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            
            endpoint = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"STK Push initiated: {data}")
            
            return data
        
        except Exception as e:
            logger.error(f"Error initiating STK push: {str(e)}")
            return {'error': str(e)}
    
    def check_transaction_status(self, checkout_request_id):
        """
        Check the status of an STK push transaction
        
        Args:
            checkout_request_id: The checkout request ID from initiate_stk_push
        
        Returns:
            dict: Response from M-Pesa API
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'error': 'Failed to get access token'}
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            import base64
            password_str = self.business_shortcode + self.passkey + timestamp
            password = base64.b64encode(password_str.encode()).decode()
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id,
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            
            endpoint = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data
        
        except Exception as e:
            logger.error(f"Error checking transaction status: {str(e)}")
            return {'error': str(e)}
    
    def process_callback(self, callback_data):
        """
        Process M-Pesa callback data
        
        Args:
            callback_data: The callback data from M-Pesa
        
        Returns:
            dict: Processed callback info
        """
        try:
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            
            result = {
                'checkout_request_id': stk_callback.get('CheckoutRequestID'),
                'result_code': stk_callback.get('ResultCode'),
                'result_description': stk_callback.get('ResultDesc'),
                'merchant_request_id': stk_callback.get('MerchantRequestID'),
                'callback_metadata': stk_callback.get('CallbackMetadata', {})
            }
            
            # Extract callback metadata items
            if result['callback_metadata']:
                items = result['callback_metadata'].get('Item', [])
                metadata = {}
                for item in items:
                    key = item.get('Name')
                    value = item.get('Value')
                    if key and value is not None:
                        metadata[key] = value
                result['metadata'] = metadata
            
            logger.info(f"Processed callback: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error processing callback: {str(e)}")
            return {'error': str(e)}


def get_mpesa_service(use_sandbox=True):
    """Factory function to get M-Pesa service instance"""
    return MpesaService(use_sandbox=use_sandbox)