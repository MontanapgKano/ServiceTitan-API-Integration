"""
Supabase-specific functions for formatting contact data
"""

import json
import re

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


def get_supabase_contacts_data():
    """
    Get contact data formatted specifically for Supabase contacts table
    Returns data with exact field names matching the Supabase table structure
    """
    print("Preparing contact data for Supabase contacts table...")
    print("-" * 60)
    
    # Import the global array from data_processor
    from data_processor import global_customer_data_array, add_phone_numbers_to_customer_records, add_location_data_to_customer_records
    
    if not global_customer_data_array:
        print("No customer data available in global array")
        return []
    
    # Ensure we have the latest data
    print("Ensuring all data is up to date...")
    add_phone_numbers_to_customer_records()
    add_location_data_to_customer_records()
    
    # Prepare data for Supabase contacts table
    supabase_contacts_data = []
    
    for customer in global_customer_data_array:
        customer_id = customer.get('customer_id')
        if not customer_id:
            continue
        
        # Extract all contact information
        phone_numbers_list = customer.get('phone_numbers', [])
        emails_list = customer.get('emails', [])
        all_addresses = customer.get('addresses', [])
        
        # Extract all address components
        all_streets = []
        all_cities = []
        all_zips = []
        all_address_names = []
        
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
                    all_address_names.append(name)
        
        # Extract all phone numbers
        all_phones = []
        for phone in phone_numbers_list:
            if phone and phone.strip():
                all_phones.append(phone.strip())
        
        # Extract all emails (with validation to ensure only valid email addresses)
        all_emails = []
        for email_obj in emails_list:
            if isinstance(email_obj, dict):
                email = email_obj.get('email', '')
                if email and is_valid_email(email):
                    all_emails.append(email.strip())
            elif isinstance(email_obj, str) and is_valid_email(email_obj):
                all_emails.append(email_obj.strip())
        
        # Format billing data
        billingname_list = customer.get('billingname', [])
        billingline1_list = customer.get('billingline1', [])
        
        # Create Supabase contacts record with exact field names
        supabase_record = {
            'customer_id': customer_id,
            'contactname': customer.get('customer_name', '') or 'No Contact Name Info',
            
            # All phone numbers (semicolon-separated)
            'all_phone_numbers': '; '.join(all_phones) if all_phones else 'No Phone Info',
            
            # All emails (semicolon-separated) - ONLY emails, no phone numbers
            'all_emails': '; '.join(all_emails) if all_emails else 'No Email Info',
            
            # All address components (semicolon-separated)
            'all_streets': '; '.join(all_streets) if all_streets else 'No Street Info',
            'all_cities': '; '.join(all_cities) if all_cities else 'No City Info',
            'all_zips': '; '.join(all_zips) if all_zips else 'No Zip Info',
            'all_addresses': '; '.join(all_address_names) if all_address_names else 'No Address Name Info',
            
            # Primary address (from latest location)
            'primary_street': customer.get('location_street', '') or 'No Street Info',
            'primary_city': customer.get('location_city', '') or 'No City Info',
            'primary_zip': customer.get('location_number', '') or 'No Zip Info',
            'primary_address': customer.get('location_name', '') or 'No Address Name Info',
            
            # Additional fields
            'is_vip': customer.get('is_vip', 'NO') or 'No VIP Info',
            'business_unit_name': customer.get('business_unit_name', '') or 'No Business Unit Info',
            
            # Billing information (JSON arrays)
            'billingname': json.dumps(billingname_list) if billingname_list else 'No Billing Name Info',
            'billingline1': json.dumps(billingline1_list) if billingline1_list else 'No Billing Line Info'
        }
        
        supabase_contacts_data.append(supabase_record)
    
    print(f"\nSupabase Contacts Data Summary:")
    print(f"  - Total customers processed: {len(supabase_contacts_data)}")
    
    # Calculate statistics
    customers_with_phones = sum(1 for record in supabase_contacts_data if record['all_phone_numbers'])
    customers_with_emails = sum(1 for record in supabase_contacts_data if record['all_emails'])
    customers_with_addresses = sum(1 for record in supabase_contacts_data if record['all_streets'])
    
    print(f"  - Customers with phone numbers: {customers_with_phones}")
    print(f"  - Customers with emails: {customers_with_emails}")
    print(f"  - Customers with addresses: {customers_with_addresses}")
    
    # Show sample data
    print(f"\nSample Supabase contacts data:")
    sample_count = min(3, len(supabase_contacts_data))
    for i in range(sample_count):
        record = supabase_contacts_data[i]
        print(f"  - Customer {record['customer_id']} ({record['contactname']}):")
        print(f"    All Phones: {record['all_phone_numbers']}")
        print(f"    All Emails: {record['all_emails']}")
        print(f"    All Streets: {record['all_streets']}")
        print(f"    All Cities: {record['all_cities']}")
        print(f"    All Zips: {record['all_zips']}")
        print(f"    All Address Names: {record['all_addresses']}")
        print(f"    Primary Address: {record['primary_street']}, {record['primary_city']} {record['primary_zip']}")
        print(f"    VIP Status: {record['is_vip']}")
        print(f"    Business Unit: {record['business_unit_name']}")
    
    print(f"SUCCESS! Prepared {len(supabase_contacts_data)} contact records for Supabase")
    return supabase_contacts_data


def export_supabase_contacts_to_csv(filename="supabase_contacts_data.csv"):
    """
    Export Supabase contacts data to CSV
    """
    import csv
    
    print(f"Exporting Supabase contacts data to {filename}...")
    
    # Get the Supabase contacts data
    data = get_supabase_contacts_data()
    
    if not data:
        print("No data to export")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Define fieldnames matching the Supabase table structure
            fieldnames = [
                'customer_id', 'contactname',
                'all_phone_numbers',
                'all_emails',
                'all_streets', 'all_cities', 'all_zips', 'all_addresses',
                'primary_street', 'primary_city', 'primary_zip', 'primary_address',
                'is_vip', 'business_unit_name',
                'billingname', 'billingline1'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for record in data:
                writer.writerow(record)
        
        print(f"Successfully exported {len(data)} records to {filename}")
        return True
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False


def test_supabase_data():
    """
    Test function to demonstrate the Supabase data format
    """
    print("Testing Supabase contacts data format...")
    print("=" * 60)
    
    # Get sample data
    data = get_supabase_contacts_data()
    
    if data:
        print(f"\nSample record structure:")
        sample_record = data[0]
        for key, value in sample_record.items():
            print(f"  {key}: {value}")
        
        print(f"\nField Summary:")
        print(f"  - customer_id: {sample_record.get('customer_id', 'N/A')}")
        print(f"  - contactname: {sample_record.get('contactname', 'N/A')}")
        print(f"  - all_phone_numbers: {sample_record.get('all_phone_numbers', 'N/A')}")
        print(f"  - all_emails: {sample_record.get('all_emails', 'N/A')}")
        print(f"  - all_streets: {sample_record.get('all_streets', 'N/A')}")
        print(f"  - all_cities: {sample_record.get('all_cities', 'N/A')}")
        print(f"  - all_zips: {sample_record.get('all_zips', 'N/A')}")
        print(f"  - all_addresses: {sample_record.get('all_addresses', 'N/A')}")
        print(f"  - primary_street: {sample_record.get('primary_street', 'N/A')}")
        print(f"  - primary_city: {sample_record.get('primary_city', 'N/A')}")
        print(f"  - primary_zip: {sample_record.get('primary_zip', 'N/A')}")
        print(f"  - primary_address: {sample_record.get('primary_address', 'N/A')}")
        print(f"  - is_vip: {sample_record.get('is_vip', 'N/A')}")
        print(f"  - business_unit_name: {sample_record.get('business_unit_name', 'N/A')}")
        print(f"  - billingname: {sample_record.get('billingname', 'N/A')}")
        print(f"  - billingline1: {sample_record.get('billingline1', 'N/A')}")
        
        return True
    else:
        print("No data available for testing")
        return False


if __name__ == "__main__":
    # Test the functions
    test_supabase_data()
