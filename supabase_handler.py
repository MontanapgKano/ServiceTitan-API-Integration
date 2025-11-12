#!/usr/bin/env python3
"""
Supabase Handler Module
Handles saving data to Supabase database
"""

import os
import time
import re
from datetime import datetime
from supabase import create_client, Client

def is_valid_email(email):
    """
    Validate if a string is a valid email address
    Returns True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip()
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Check if it matches email pattern and is not just digits
    return bool(re.match(email_pattern, email)) and not email.isdigit()
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', "")
SUPABASE_KEY = os.getenv('SUPABASE_KEY', "")
SUPABASE_TABLE_NAME = os.getenv('SUPABASE_TABLE_NAME', 'test_contacts')

# Global Supabase client instance (initialized once)
_supabase_client = None


def validate_supabase_config():
    """
    Validate that required Supabase configuration values are set.
    Returns True if valid, False otherwise.
    """
    required_vars = [
        ('SUPABASE_URL', SUPABASE_URL),
        ('SUPABASE_KEY', SUPABASE_KEY)
    ]
    
    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value or var_value.startswith('your_'):
            missing_vars.append(var_name)
    
    if missing_vars:
        print("ERROR: Missing or invalid Supabase configuration values:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nCONFIG: Please update your .env file with the correct values.")
        return False
    
    return True


def print_supabase_config_summary():
    """Print a summary of current Supabase configuration (with masked sensitive values)."""
    print("INFO: Supabase Configuration:")
    print(f"   - URL: {SUPABASE_URL[:20]}...{SUPABASE_URL[-10:] if len(SUPABASE_URL) > 30 else '***'}")
    print(f"   - Table: {SUPABASE_TABLE_NAME}")


def get_supabase_client():
    """
    Get the global Supabase client instance, creating it if it doesn't exist
    """
    global _supabase_client
    
    if _supabase_client is None:
        try:
            print("CONNECT: Creating Supabase client...")
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("SUCCESS: Supabase client created successfully")
                
        except Exception as e:
            print(f"ERROR: Error creating Supabase client: {e}")
            _supabase_client = None
            return None
    
    return _supabase_client


def prepare_customer_for_database(customer_data):
    """
    Prepare customer data for database insertion/update
    Works with combined customer-location data structure
    Returns: dict with database-ready customer data matching the current table schema
    """
    # Extract fields from combined data structure
    customer_id = customer_data.get('customer_id')
    
    # Extract phone number and email
    phone = customer_data.get('phone_number', '')
    if not phone:
        phone = 'No Phone Number'
    
    email = customer_data.get('email', '')
    if not email:
        email = 'No Email Address'
  
    
    # Extract location tag type names
    
    # Extract customer name and billing fields
    contactname = customer_data.get('customer_name', '')
    billingname = customer_data.get('billingname', [])
    billingline1 = customer_data.get('billingline1', [])
    
    # Extract VIP status
    is_vip = customer_data.get('is_vip', 'NO')
    
    # Extract business unit  name
    business_unit_name = customer_data.get('business_unit_name', '')
    
    # Extract location address components (using new field names)
    primary_street = customer_data.get('location_street', '')
    primary_city = customer_data.get('location_city', '')
    primary_zip = customer_data.get('location_number', '')
    
    # Extract all contact information
    phone_numbers_list = customer_data.get('phone_numbers', [])
    emails_list = customer_data.get('emails', [])
    all_addresses = customer_data.get('addresses', [])
    
    # Format all phone numbers (semicolon-separated)
    all_phones = []
    for phone in phone_numbers_list:
        if phone and phone.strip():
            all_phones.append(phone.strip())
    all_phone_numbers = '; '.join(all_phones) if all_phones else 'No Phone Info'
    
    # Format all emails (semicolon-separated) - ONLY valid email addresses, no phone numbers
    all_emails = []
    for email_obj in emails_list:
        if isinstance(email_obj, dict):
            email_addr = email_obj.get('email', '')
            if email_addr and is_valid_email(email_addr):
                all_emails.append(email_addr.strip())
        elif isinstance(email_obj, str) and is_valid_email(email_obj):
            all_emails.append(email_obj.strip())
    all_emails_str = '; '.join(all_emails) if all_emails else 'No Email Info'
    
    # Extract all address components
    all_streets = []
    all_cities = []
    all_zips = []
    all_addresses = []
    
    for address in all_addresses:
        if isinstance(address, dict):
            street = address.get('street', '')
            city = address.get('city', '')
            zip_code = address.get('zip', '')
            name = address.get('name', '')
            
            if street:
                all_streets.append(street)
            if city:
                all_cities.append(city)
            if zip_code:
                all_zips.append(zip_code)
            if name:
                all_addresses.append(name)
    
    # Get primary address name
    primary_address = customer_data.get('location_name', '') or 'No Address Name Info'
    
    return {
        'customer_id': customer_id,
        'contactname': contactname or 'No Contact Name Info',
        
        # All phone numbers
        'all_phone_numbers': all_phone_numbers,
        
        # All emails
        'all_emails': all_emails_str,
        
        # All address components
        'all_streets': '; '.join(all_streets) if all_streets else 'No Street Info',
        'all_cities': '; '.join(all_cities) if all_cities else 'No City Info',
        'all_zips': '; '.join(all_zips) if all_zips else 'No Zip Info',
        'all_addresses': '; '.join(all_addresses) if all_addresses else 'No Address Name Info',
        
        # Primary address (latest)
        'primary_street': primary_street or 'No Street Info',
        'primary_city': primary_city or 'No City Info',
        'primary_zip': primary_zip or 'No Zip Info',
        'primary_address': primary_address,
        
        # Additional fields
        'is_vip': is_vip or 'No VIP Info',
        'business_unit_name': business_unit_name or 'No Business Unit Info',
        
        # Billing information (JSON arrays)
        'billingname': str(billingname) if billingname else 'No Billing Name Info',
        'billingline1': str(billingline1) if billingline1 else 'No Billing Line Info',
        
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }


def insert_or_update_customer(customer_data):
    """
    Insert or update a single customer in Supabase
    Works with global array data structure
    Returns: ('inserted', customer_data), ('updated', customer_data), or ('error', customer_data)
    """
    try:
        customer_id = customer_data.get('customer_id')
        # Use customer_id as name for logging since we don't have name in global array
        customer_name = f"Customer {customer_id}" if customer_id else "Unknown"
        
        if not customer_id:
            print(f"    WARNING: Skipping customer: No customer ID found")
            return 'error', customer_data
        
        # Prepare customer data for database
        prepared_customer = prepare_customer_for_database(customer_data)
        
        # Insert/Update in Supabase with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                supabase = get_supabase_client()
                if not supabase:
                    print(f"    ERROR: Failed to get Supabase client for {customer_name}")
                    return 'error', customer_data
                
                # Check if customer exists in database (using customer_id as unique identifier)
                customer_id = prepared_customer.get('customer_id', '')
                if customer_id:
                    existing_customer = supabase.table(SUPABASE_TABLE_NAME).select('*').eq('customer_id', customer_id).execute()
                    
                    if existing_customer.data and len(existing_customer.data) > 0:
                        # Customer exists - update the record
                        update_data = {k: v for k, v in prepared_customer.items() if k != 'created_at'}
                        result = supabase.table(SUPABASE_TABLE_NAME).update(update_data).eq('customer_id', customer_id).execute()
                        
                        if result.data:
                            print(f"     Updated {customer_name} (ID: {customer_id})")
                            return 'updated', customer_data
                        else:
                            print(f"    ERROR: Failed to update {customer_name} (ID: {customer_id})")
                            return 'error', customer_data
                    else:
                        # Customer doesn't exist - insert new record
                        result = supabase.table(SUPABASE_TABLE_NAME).insert(prepared_customer).execute()
                        
                        if result.data:
                            print(f"     Inserted {customer_name} (ID: {customer_id})")
                            return 'inserted', customer_data
                        else:
                            print(f"    ERROR: Failed to insert {customer_name} (ID: {customer_id})")
                            return 'error', customer_data
                else:
                    # No customer_id available - insert new record
                    result = supabase.table(SUPABASE_TABLE_NAME).insert(prepared_customer).execute()
                    
                    if result.data:
                        print(f"     Inserted {customer_name} (No ID)")
                        return 'inserted', customer_data
                    else:
                        print(f"    ERROR: Failed to insert {customer_name} (No ID)")
                        return 'error', customer_data
                        
            except Exception as db_error:
                print(f"    WARNING: Database error for {customer_name} (attempt {attempt + 1}/{max_retries}): {db_error}")
                if attempt < max_retries - 1:
                    print(f"     Retrying in 2 seconds...")
                    time.sleep(1)
                else:
                    print(f"    ERROR: All database attempts failed for {customer_name}")
                    return 'error', customer_data
                
    except Exception as e:
        print(f"    ERROR: Error processing customer {customer_name}: {e}")
        return 'error', customer_data


def save_customers_to_supabase(customers_data):
    """
    Save a list of customers to Supabase database
    Returns: dict with summary of operations
    """
    if not customers_data:
        print("ERROR: No customer data provided to save")
        return {
            'success': False,
            'total_processed': 0,
            'total_inserted': 0,
            'total_updated': 0,
            'total_errors': 0
        }
    
    print(f" Saving {len(customers_data)} customers to Supabase...")
    print("-" * 50)
    
    total_inserted = 0
    total_updated = 0
    total_errors = 0
    
    for i, customer_data in enumerate(customers_data, 1):
        customer_id = customer_data.get('customer_id', 'Unknown')
        print(f"Processing customer {i}/{len(customers_data)}: Customer {customer_id}")
        
        result, _ = insert_or_update_customer(customer_data)
        
        if result == 'inserted':
            total_inserted += 1
        elif result == 'updated':
            total_updated += 1
        else:
            total_errors += 1
    
    summary = {
        'success': total_errors < len(customers_data),
        'total_processed': len(customers_data),
        'total_inserted': total_inserted,
        'total_updated': total_updated,
        'total_errors': total_errors
    }
    
    print("-" * 50)
    print(f"STATS: Supabase Save Summary:")
    print(f"  - Total customers processed: {summary['total_processed']}")
    print(f"  - New customers inserted: {summary['total_inserted']}")
    print(f"  - Existing customers updated: {summary['total_updated']}")
    print(f"  - Errors encountered: {summary['total_errors']}")
    
    if summary['success']:
        print("SUCCESS: All customers saved successfully to Supabase!")
    else:
        print("WARNING: Some customers failed to save to Supabase")
    
    return summary


def initialize_supabase_connection():
    """
    Initialize Supabase connection and test it
    Returns: True if successful, False otherwise
    """
    print("CONNECT: Initializing Supabase Connection")
    print("=" * 50)
    
    # Validate configuration
    if not validate_supabase_config():
        return False
    
    # Print configuration summary
    print_supabase_config_summary()
    
    print("SUCCESS: Supabase connection initialized successfully!")
    return True
