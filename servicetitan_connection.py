#!/usr/bin/env python3
"""
ServiceTitan API Connection Module
Handles authentication, token management, and API requests to ServiceTitan
"""

import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# ServiceTitan API Configuration
SERVICETITAN_TENANT_ID = os.getenv('SERVICETITAN_TENANT_ID', "")
SERVICETITAN_CLIENT_ID = os.getenv('SERVICETITAN_CLIENT_ID', "")
SERVICETITAN_CLIENT_SECRET = os.getenv('SERVICETITAN_CLIENT_SECRET', "")
SERVICETITAN_APP_KEY = os.getenv('SERVICETITAN_APP_KEY', "")

# Global token management
_token_info = {
    'access_token': None,
    'expires_at': None,
    'tenant_id': None,
    'client_id': None,
    'client_secret': None,
    'app_key': None,
    'scope': ''
}


def validate_servicetitan_config():
    """
    Validate that required ServiceTitan configuration values are set.
    Returns True if valid, False otherwise.
    """
    required_vars = [
        ('SERVICETITAN_TENANT_ID', SERVICETITAN_TENANT_ID),
        ('SERVICETITAN_CLIENT_ID', SERVICETITAN_CLIENT_ID), 
        ('SERVICETITAN_CLIENT_SECRET', SERVICETITAN_CLIENT_SECRET),
        ('SERVICETITAN_APP_KEY', SERVICETITAN_APP_KEY)
    ]
    
    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value or var_value.startswith('your_'):
            missing_vars.append(var_name)
    
    if missing_vars:
        print("ERROR: Missing or invalid ServiceTitan configuration values:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nCONFIG: Please update your .env file with the correct values.")
        return False
    
    return True


def print_servicetitan_config_summary():
    """Print a summary of current ServiceTitan configuration (with masked sensitive values)."""
    print("ServiceTitan Configuration:")
    print(f"   - Tenant ID: {SERVICETITAN_TENANT_ID}")
    print(f"   - Client ID: {SERVICETITAN_CLIENT_ID[:8]}...{SERVICETITAN_CLIENT_ID[-4:] if len(SERVICETITAN_CLIENT_ID) > 12 else '***'}")
    print(f"   - App Key: {SERVICETITAN_APP_KEY[:8]}...{SERVICETITAN_APP_KEY[-4:] if len(SERVICETITAN_APP_KEY) > 12 else '***'}")


def get_auth_token(tenant_id, client_id, client_secret, scope="", app_key=None):
    """
    Get authentication token from ServiceTitan API using proper OAuth credentials
    Returns: dict with access_token, expires_in, and other token info
    """
    
    # API endpoint
    url = "https://auth.servicetitan.io/connect/token"
    
    # Headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Form data for OAuth 2.0 Client Credentials Grant
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope
    }
    
    try:
        print(f"Authenticating with ServiceTitan API...")
        print(f"Tenant ID: {tenant_id}")
        print(f"Client ID: {client_id[:8]}...{client_id[-4:]}")  # Masked for security
        print(f"Scope: {scope}")
        
        response = requests.post(url, headers=headers, data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            json_response = response.json()
            print("SUCCESS: Authentication successful!")
            
            access_token = json_response.get('access_token')
            expires_in = json_response.get('expires_in', 3600)  # Default to 1 hour
            
            if access_token:
                print(f"Access Token: {access_token[:50]}...")  # Show first 50 chars
                print(f"Token expires in: {expires_in} seconds")
                
                # Calculate expiry time
                expires_at = datetime.now().timestamp() + expires_in
                
                # Store token info globally
                global _token_info
                _token_info.update({
                    'access_token': access_token,
                    'expires_at': expires_at,
                    'tenant_id': tenant_id,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'app_key': app_key,
                    'scope': scope
                })
                
                return {
                    'access_token': access_token,
                    'expires_in': expires_in,
                    'expires_at': expires_at,
                    'token_type': json_response.get('token_type', 'Bearer')
                }
            else:
                print("ERROR: No access_token in response")
                print(f"Response: {json_response}")
                return None
        else:
            print(f"ERROR: Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Error parsing JSON response: {e}")
        return None


def is_token_expired():
    """
    Check if the current token is expired or will expire soon (within 5 minutes)
    """
    global _token_info
    
    if not _token_info.get('access_token') or not _token_info.get('expires_at'):
        return True
    
    # Check if token expires within 2 minutes (120 seconds)
    buffer_time = 120
    current_time = datetime.now().timestamp()
    
    return current_time >= (_token_info['expires_at'] - buffer_time)


def get_valid_token():
    """
    Get a valid access token, refreshing if necessary
    Returns: access_token string or None if failed
    """
    global _token_info
    
    # Check if we have a valid token that's not expired
    if not is_token_expired():
        return _token_info['access_token']
    
    # Token is expired or missing, need to refresh
    print("PROCESS: Token expired or missing, refreshing...")
    
    # Get stored credentials
    tenant_id = _token_info.get('tenant_id')
    client_id = _token_info.get('client_id')
    client_secret = _token_info.get('client_secret')
    app_key = _token_info.get('app_key')
    scope = _token_info.get('scope', '')
    
    if not all([tenant_id, client_id, client_secret]):
        print("ERROR: Missing credentials for token refresh")
        print(f"   - tenant_id: {'SUCCESS: Yes' if tenant_id else 'ERROR: No'}")
        print(f"   - client_id: {'SUCCESS: Yes' if client_id else 'ERROR: No'}")
        print(f"   - client_secret: {'SUCCESS: Yes' if client_secret else 'ERROR: No'}")
        return None
    
    # Try to get a new token
    print(f"AUTH: Attempting token refresh for tenant: {tenant_id}")
    token_result = get_auth_token(tenant_id, client_id, client_secret, scope, app_key)

    if token_result and token_result.get('access_token'):
        print("SUCCESS: Token refreshed successfully!")
        return token_result['access_token']
    else:
        print("ERROR: Failed to refresh token")
        return None


def make_api_request_with_retry(url, headers, params=None, method='GET', max_retries=2):
    """
    Make an API request with automatic token refresh on 401 errors
    Returns: (response, success) tuple
    """
    for attempt in range(max_retries + 1):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=params, timeout=30)
            else:
                response = requests.request(method, url, headers=headers, params=params, timeout=30)
            
            # If we get a 401, try to refresh the token and retry
            if response.status_code == 401 and attempt < max_retries:
                print(f"    WARNING: Got 401 error, refreshing token and retrying (attempt {attempt + 1}/{max_retries + 1})")
                print(f"    INFO: Response: {response.text[:200]}...")
                
                # Force token refresh by clearing the current token
                global _token_info
                _token_info['access_token'] = None
                _token_info['expires_at'] = None
                
                # Get a new token
                new_token = get_valid_token()
                if new_token:
                    # Update headers with new token
                    headers['Authorization'] = f"Bearer {new_token}"
                    print(f"    SUCCESS: Token refreshed, retrying request...")
                    continue
                else:
                    print(f"    ERROR: Failed to refresh token on attempt {attempt + 1}")
                    return response, False
            
            return response, True
            
        except requests.exceptions.RequestException as e:
            print(f"    ERROR: Request error on attempt {attempt + 1}: {e}")
            if attempt == max_retries:
                return None, False
            time.sleep(0.5)  # Brief delay before retry
    
    return None, False


def get_api_headers(tenant_id, app_key=None):
    """
    Get standard API headers with valid token
    Returns: headers dict or None if failed
    """
    valid_token = get_valid_token()
    if not valid_token:
        return None
    
    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    
    if app_key:
        headers["ST-App-Key"] = app_key
    
    return headers


def get_fresh_api_headers(tenant_id, app_key=None):
    """
    Get API headers with a valid token (only refresh if expired)
    This ensures we have a valid token without unnecessary refreshes
    Returns: headers dict or None if failed
    """
    # Only refresh token if it's actually expired or missing
    # Don't force refresh on every call
    return get_api_headers(tenant_id, app_key)


def initialize_servicetitan_connection():
    """
    Initialize ServiceTitan connection with authentication
    Returns: (access_token, tenant_id, app_key) or (None, None, None) if failed
    """
    print("AUTH: Initializing ServiceTitan Connection")
    print("=" * 50)
    
    # Validate configuration
    if not validate_servicetitan_config():
        return None, None, None
    
    # Print configuration summary
    print_servicetitan_config_summary()
    
    # Authenticate
    required_scopes = ""
    print(f"Scope: '{required_scopes}'")
    print("-" * 50)
    
    token_result = get_auth_token(
        SERVICETITAN_TENANT_ID, 
        SERVICETITAN_CLIENT_ID, 
        SERVICETITAN_CLIENT_SECRET, 
        required_scopes, 
        SERVICETITAN_APP_KEY
    )
    
    if token_result and token_result.get('access_token'):
        print("SUCCESS: ServiceTitan connection initialized successfully!")
        return token_result['access_token'], SERVICETITAN_TENANT_ID, SERVICETITAN_APP_KEY
    else:
        print("ERROR: Failed to initialize ServiceTitan connection")
        return None, None, None


def validate_token_realtime():
    """
    Real-time token validation with detailed logging
    Returns: True if token is valid, False otherwise
    """
    global _token_info
    
    print("AUTH: Real-time token validation...")
    
    if not _token_info.get('access_token'):
        print("ERROR: No access token found")
        return False
    
    if not _token_info.get('expires_at'):
        print("ERROR: No expiration time found")
        return False
    
    current_time = datetime.now().timestamp()
    expires_at = _token_info['expires_at']
    time_until_expiry = expires_at - current_time
    
    print(f"INFO: Token expires in: {time_until_expiry:.0f} seconds")
    
    if time_until_expiry <= 0:
        print("ERROR: Token has expired")
        return False
    elif time_until_expiry <= 120:  # 2 minutes
        print("WARNING: Token expires soon, will refresh on next request")
        return False
    else:
        print("SUCCESS: Token is valid")
        return True


def force_token_refresh():
    """
    Force a token refresh regardless of expiration status
    Returns: True if successful, False otherwise
    """
    global _token_info
    
    print("PROCESS: Forcing token refresh...")
    
    # Get stored credentials
    tenant_id = _token_info.get('tenant_id')
    client_id = _token_info.get('client_id')
    client_secret = _token_info.get('client_secret')
    app_key = _token_info.get('app_key')
    scope = _token_info.get('scope', '')
    
    if not all([tenant_id, client_id, client_secret]):
        print("ERROR: Missing credentials for forced token refresh")
        return False
    
    # Force token refresh
    token_result = get_auth_token(tenant_id, client_id, client_secret, scope, app_key)
    
    if token_result and token_result.get('access_token'):
        print("SUCCESS: Token refresh successful")
        return True
    else:
        print("ERROR: Token refresh failed")
        return False
