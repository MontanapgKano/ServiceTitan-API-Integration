import requests
import json
import time
import re
from servicetitan_connection import get_valid_token, make_api_request_with_retry, get_api_headers, get_fresh_api_headers, validate_token_realtime, force_token_refresh

global_customer_data_array = []

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

customer_ids = []

contacts = []

# Local variable to store locations data
locations = []


# Local variable to store invoices data
invoices = []

# Local variable to store memberships data
memberships = []

# Local variable to store jobs data
jobs = []

# Local variable to store job types data
business_units = []

max_pages = 1


def get_global_customer_data():
    """
    Get the current global customer data array
    Returns: list of customer records
    """
    return global_customer_data_array.copy()


def extract_customer_ids():
    """
    Extract all customer_id values from global_customer_data_array and store in customer_ids
    Returns: list of customer IDs
    """
    global customer_ids
    
    # Clear existing customer IDs
    customer_ids.clear()
    
    # Extract customer IDs from global array
    for customer_record in global_customer_data_array:
        customer_id = customer_record.get('customer_id')
        if customer_id:
            customer_ids.append(customer_id)
    print(f"INFO: Extracted {len(customer_ids)} customer IDs from global array")
    return customer_ids.copy()


def get_customer_ids():
    """
    Get the current customer IDs list
    Returns: list of customer IDs
    """
    return customer_ids.copy()


def get_contacts_data():
    """
    Get the current contacts data from local array
    Returns: list of contacts
    """
    return contacts.copy()


def get_locations_data():
    """
    Get the current locations data from local array
    Returns: list of locations
    """
    return locations.copy()




def get_invoices_data():
    """
    Get the current invoices data from local array
    Returns: list of invoices
    """
    return invoices.copy()


def get_memberships_data():
    """
    Get the current memberships data from local array
    Returns: list of memberships
    """
    return memberships.copy()


def get_jobs_data():
    """
    Get the current jobs data from local array
    Returns: list of jobs
    """
    return jobs.copy()


def get_business_units_data():
    """
    Get the current business units data from local array
    Returns: list of business units
    """
    return business_units.copy()


def get_customers(tenant_id, app_key=None, page_size=200):
    """
    Retrieve customer data from ServiceTitan API with specific fields extracted
    Stores data in global_customer_data_array
    Returns: success status and summary
    """
    
    # API endpoint for customers
    base_url = f"https://api.servicetitan.io/crm/v2/tenant/{tenant_id}/customers"
    
    # Get a valid token (will refresh if needed)
    valid_token = get_valid_token()
    if not valid_token:
        print("ERROR: Failed to get valid token for customers")
        return None
    
    # Headers with authorization
    headers = get_api_headers(tenant_id, app_key)
    if not headers:
        return None
    
    # Initialize counters
    total_customers_processed = 0
    page = 1
    
    try:
        print(f"STATS: Retrieving customer data from: {base_url}")
        print(f"INFO: Page size: {page_size}")
        print("PROCESS: Fetching customers and storing in global array...")
        print("-" * 60)
        
        while page <= 10:
            # Get headers with valid token (only refresh if expired)
            fresh_headers = get_fresh_api_headers(tenant_id, app_key)
            if not fresh_headers:
                print(f"ERROR: Failed to get fresh headers for customers page {page}")
                return None
            
            # Add pagination parameters
            params = {
                "page": page,
                "pageSize": page_size
            }
            
            print(f"INFO: Fetching page {page}/{max_pages}...")
            response, success = make_api_request_with_retry(base_url, fresh_headers, params)
            
            if not success or not response:
                print(f"ERROR: Failed to make API request for customers page {page}")
                return None
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                json_response = response.json()
                customers = json_response.get('data', [])
                pagination = json_response.get('pagination', {})
                
                # Process each customer as they are fetched
                customer_count = len(customers)
                has_more = pagination.get('hasMore', False)
                
                print(f"INFO: Page {page}: Retrieved {customer_count} customers")
                
                # Process each customer to extract specific fields
                for customer in customers:
                    # Extract specific fields
                    customer_id = customer.get('id')
                    customer_name = customer.get('name')  # Extract customer name
                    address = customer.get('address', {})
                    
                    # Extract address fields
                    address_street = ''
                    address_city = ''
                    
                    if isinstance(address, dict):
                        address_street = address.get('street', '')
                        address_city = address.get('city', '')
                    elif isinstance(address, str):
                        address_street = address
                    
                    # Add to global array with the specific fields you requested
                    global_customer_record = {
                        'customer_id': customer_id,
                        'customer_name': customer_name,
                        'customer_address_street': address_street,
                        'customer_address_city': address_city,
                    }
                    global_customer_data_array.append(global_customer_record)
                    
                    total_customers_processed += 1
                
                print(f"SUCCESS: Page {page}: Added {customer_count} customers (Total: {total_customers_processed})")
                
                # Check if there are more pages
                if customer_count == 0:
                    print(f"WARNING: No customers returned on page {page}. Fetch complete!")
                    break
                elif customer_count < page_size:
                    print(f"WARNING: Partial page ({customer_count} customers). Reached end of data!")
                    break
                elif 'hasMore' in pagination and not has_more:
                    print(f"WARNING: API indicates no more pages (hasMore=False). Fetch complete!")
                    break
                else:
                    # Continue to next page
                    print(f"SUCCESS: Full page retrieved ({page_size} customers). Continuing to next page...")
                page += 1
                
            else:
                if response.status_code == 404:
                    print(f"WARNING: Page {page} not found - reached end of data. Fetch complete!")
                    break
                else:
                    print(f"ERROR: Error retrieving customers on page {page}: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
        
        # Extract customer IDs after populating global array
        extract_customer_ids()
        
        # Print final summary
        print(f"\nSTATS: Fetch Summary:")
        print(f"  - Total customers fetched: {total_customers_processed}")
        print(f"  - Pages processed: {page}")
        print(f"  - Customers stored in global array: {total_customers_processed}")
        print(f"  - Customer IDs extracted: {len(customer_ids)}")
        
        # Return success status and summary
        result = {
            "summary": {
                "total_processed": total_customers_processed,
                "pages_processed": page,
                "customer_ids_extracted": len(customer_ids)
            },
            "success": total_customers_processed > 0
        }
        
        print(f"SUCCESS: Stored {total_customers_processed} customers in global array across {page} pages")
        return result
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return None


def get_customer_contacts(tenant_id, app_key=None, page_size=200):
    """
    Fetch customer contacts from ServiceTitan API in batches and store in local contacts array
    API endpoint: https://api.servicetitan.io/crm/v2/tenant/{tenant_id}/customers/contacts
    Extracts only phoneNumber from phoneSettings and customerId
    Processes customer IDs in batches of page_size to avoid API issues
    Returns: success status and summary
    """
    
    print("CONTACTS: Fetching customer contacts and storing in local array...")
    print("-" * 60)
    
    # Check if customer_ids array is populated
    if not customer_ids:
        print("ERROR: No customer IDs available. Please fetch customers first.")
        return None
    
    # Clear the local contacts array before fetching new data
    global contacts
    contacts.clear()
    
    # API endpoint for customer contacts
    base_url = f"https://api.servicetitan.io/crm/v2/tenant/{tenant_id}/customers/contacts"
    
    # Get a valid token
    valid_token = get_valid_token()
    if not valid_token:
        print("ERROR: Failed to get valid token for contacts fetching")
        return None
    
    # Headers with authorization
    headers = get_api_headers(tenant_id, app_key)
    if not headers:
        return None
    
    # Initialize counters
    total_contacts_processed = 0
    total_batches_processed = 0
    
    try:
        print(f"STATS: Retrieving contacts data from: {base_url}")
        print(f"INFO: Batch size: {page_size} customer IDs per request")
        print(f"INFO: Total customer IDs to process: {len(customer_ids)}")
        print("PROCESS: Fetching customer contacts in batches...")
        print("-" * 60)
        
        # Process customer IDs in batches of page_size
        for batch_start in range(0, len(customer_ids), page_size):
            batch_end = min(batch_start + page_size, len(customer_ids))
            batch_customer_ids = customer_ids[batch_start:batch_end]
            batch_number = (batch_start // page_size) + 1
            total_batches = (len(customer_ids) + page_size - 1) // page_size
            
            print(f"BATCH: Processing batch {batch_number}/{total_batches} ({len(batch_customer_ids)} customer IDs)")
            print(f"INFO: Customer IDs in this batch: {batch_customer_ids[:5]}{'...' if len(batch_customer_ids) > 5 else ''}")
            
            # Get headers with valid token (only refresh if expired)
            fresh_headers = get_fresh_api_headers(tenant_id, app_key)
            if not fresh_headers:
                print(f"ERROR: Failed to get fresh headers for batch {batch_number}")
                continue
            
            # Add parameters for this batch
            params = {
                "page": 1,  # Always use page 1 for batch requests
                "pageSize": 100,  # Use a reasonable page size for contacts
                "customerIds": ",".join([str(customer_id) for customer_id in batch_customer_ids])
            }
            
            response, success = make_api_request_with_retry(base_url, fresh_headers, params)
            
            if not success or not response:
                print(f"ERROR: Failed to make API request for batch {batch_number}")
                continue
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                json_response = response.json()
                contacts_data = json_response.get('data', [])
                
                # Process each contact and extract only phoneNumber and customerId
                batch_contacts_processed = 0
                for contact in contacts_data:
                    # Extract only the fields we need
                    customer_id = contact.get('customerId')
                    phone_settings = contact.get('phoneSettings', {})
                    phone_number = phone_settings.get('phoneNumber', '') if phone_settings else ''
                    email = contact.get('value');
                    type = contact.get('type');
                    # Create simplified contact record with only the required fields
                    contact_record = {
                        'customerId': customer_id,
                        'phoneNumber': phone_number,
                        'email': email,
                        'type': type
                    }
                    
                    # Store the simplified contact data
                    contacts.append(contact_record)
                    batch_contacts_processed += 1
                    total_contacts_processed += 1
                
                print(f"SUCCESS: Batch {batch_number}: Added {batch_contacts_processed} contacts (Total: {total_contacts_processed})")
                total_batches_processed += 1
                
            else:
                print(f"     Error retrieving contacts for batch {batch_number}: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                # Continue with next batch instead of failing completely
                continue
        
        # Print final summary
        print(f"\nContacts Fetch Summary:")
        print(f"  - Total contacts processed: {total_contacts_processed}")
        print(f"  - Batches processed: {total_batches_processed}")
        print(f"  - Contacts stored in local array: {len(contacts)}")
        print(f"  - Customer IDs processed: {len(customer_ids)}")
        
        # Show which customers have contacts
        customers_with_contacts = set()
        for contact in contacts:
            customer_id = contact.get('customerId')
            if customer_id:
                customers_with_contacts.add(customer_id)
        
        print(f"  - Customers with contacts found: {len(customers_with_contacts)}")
        print(f"  - Customers without contacts: {len(customer_ids) - len(customers_with_contacts)}")
        
        # Return success status and summary
        result = {
            "summary": {
                "total_processed": total_contacts_processed,
                "batches_processed": total_batches_processed,
                "contacts_stored": len(contacts),
                "customer_ids_processed": len(customer_ids),
                "customers_with_contacts": len(customers_with_contacts)
            },
            "success": total_contacts_processed > 0
        }
        
        print(f" SUCCESS! Fetched {total_contacts_processed} contacts and stored {len(contacts)} in local array")
        return result
                
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return None


def get_locations(tenant_id, app_key=None, page_size=200):
    """
    Fetch all locations from ServiceTitan API and store in local locations array
    API endpoint: https://api.servicetitan.io/crm/v2/tenant/{tenant_id}/locations
    Extracts only customerId and address
    Fetches ALL locations using pagination, then filters by customer IDs
    Returns: success status and summary
    """
    
    print("LOCATIONS: Fetching ALL locations and storing in local array...")
    print("-" * 60)
    
    # Clear the local locations array before fetching new data
    global locations
    locations.clear()
    
    # API endpoint for locations
    base_url = f"https://api.servicetitan.io/crm/v2/tenant/{tenant_id}/locations"
    
    # Get a valid token
    valid_token = get_valid_token()
    if not valid_token:
        print(" Failed to get valid token for locations fetching")
        return None
    
    # Headers with authorization
    headers = get_api_headers(tenant_id, app_key)
    if not headers:
        return None
    
    # Initialize counters
    total_locations_processed = 0
    page = 1
    
    try:
        print(f" Retrieving ALL locations data from: {base_url}")
        print(f"INFO: Page size: {page_size}")
        print(" Fetching all locations using pagination...")
        print("-" * 60)
        
        while page <= 10:  # Continue until no more pages or max pages reached
            # Get headers with valid token (only refresh if expired)
            fresh_headers = get_fresh_api_headers(tenant_id, app_key)
            if not fresh_headers:
                print(f" Failed to get fresh headers for locations page {page}")
                return None
            
            # Add pagination parameters - NO customer filtering here
            params = {
                "page": page,
                "pageSize": page_size
            }
            
            print(f"INFO: Fetching locations page {page}...")
            response, success = make_api_request_with_retry(base_url, fresh_headers, params)
            
            if not success or not response:
                print(f" Failed to make API request for locations page {page}")
                return None
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                json_response = response.json()
                locations_data = json_response.get('data', [])
                pagination = json_response.get('pagination', {})
                
                # Process each location as they are fetched
                location_count = len(locations_data)
                has_more = pagination.get('hasMore', False)
                
                print(f"INFO: Page {page}: Retrieved {location_count} locations")
                
                # Process each location and extract customerId, address, and date fields
                for location in locations_data:
                    # Extract the fields we need
                    customer_id = location.get('customerId')
                    name = location.get('name')
                    address = location.get('address', {})
                    created_on = location.get('createdOn')
                    modified_on = location.get('modifiedOn')
                    # Create location record with date fields for latest location determination
                    location_record = {
                        'customerId': customer_id,
                        'name': name,
                        'address': address,
                        'createdOn': created_on,
                        'modifiedOn': modified_on
                    }
                    
                    # Store the simplified location data
                    locations.append(location_record)
                    total_locations_processed += 1
                
                print(f" Page {page}: Added {location_count} locations (Total: {total_locations_processed})")
                
                # Check if there are more pages
                if location_count == 0:
                    print(f" No locations returned on page {page}. Fetch complete!")
                    break
                elif location_count < page_size:
                    print(f" Partial page ({location_count} locations). Reached end of data!")
                    break
                elif 'hasMore' in pagination and not has_more:
                    print(f" API indicates no more pages (hasMore=False). Fetch complete!")
                    break
                else:
                    # Continue to next page
                    print(f" Full page retrieved ({page_size} locations). Continuing to next page...")
                
                # Increment page counter
                page += 1
                
                # Safety check to prevent infinite loops
                if page > 10:
                    print(f" Reached maximum page limit ({max_pages}). Stopping pagination.")
                    break
                
            else:
                if response.status_code == 404:
                    print(f" Page {page} not found - reached end of data. Fetch complete!")
                    break
                else:
                    print(f" Error retrieving locations on page {page}: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
        
        # Now filter locations by customer IDs if we have them
        if customer_ids:
            print(f"\n Filtering {len(locations)} locations by {len(customer_ids)} customer IDs...")
            filtered_locations = []
            for location in locations:
                customer_id = location.get('customerId')
                if customer_id in customer_ids:
                    filtered_locations.append(location)
            
            print(f" Filtered to {len(filtered_locations)} locations matching customer IDs")
            locations.clear()
            locations.extend(filtered_locations)
        
        # Print final summary
        print(f"\n Locations Fetch Summary:")
        print(f"  - Total locations processed: {total_locations_processed}")
        print(f"  - Pages processed: {page}")
        print(f"  - Locations stored in local array: {len(locations)}")
        print(f"  - Customer IDs available: {len(customer_ids) if customer_ids else 'N/A'}")
        
        # Show which customers have locations
        customers_with_locations = set()
        for location in locations:
            customer_id = location.get('customerId')
            if customer_id:
                customers_with_locations.add(customer_id)
        
        print(f"  - Customers with locations found: {len(customers_with_locations)}")
        if customer_ids:
            print(f"  - Customers without locations: {len(customer_ids) - len(customers_with_locations)}")
        
        # Return success status and summary
        result = {
            "summary": {
                "total_processed": total_locations_processed,
                "pages_processed": page,
                "locations_stored": len(locations),
                "customer_ids_available": len(customer_ids) if customer_ids else 0,
                "customers_with_locations": len(customers_with_locations)
            },
            "success": total_locations_processed > 0
        }
        
        print(f" SUCCESS! Fetched {total_locations_processed} locations and stored {len(locations)} in local array")
        return result
                     
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return None




def get_invoices(tenant_id, app_key=None, page_size=200):
    """
    Fetch all invoices from ServiceTitan API and store in local invoices array
    API endpoint: https://api.servicetitan.io/accounting/v2/tenant/{tenant_id}/invoices
    Extracts only referenceNumber and customer["id"]
    Returns: success status and summary
    """
    
    print("INVOICES: Fetching invoices and storing in local array...")
    print("-" * 60)
    
    # Clear the local invoices array before fetching new data
    global invoices
    invoices.clear()
    
    # API endpoint for invoices
    base_url = f"https://api.servicetitan.io/accounting/v2/tenant/{tenant_id}/invoices"
    
    # Get a valid token
    valid_token = get_valid_token()
    if not valid_token:
        print(" Failed to get valid token for invoices fetching")
        return None
    
    # Headers with authorization
    headers = get_api_headers(tenant_id, app_key)
    if not headers:
        return None
    
    # Initialize counters
    total_invoices_processed = 0
    page = 1
    
    try:
        print(f" Retrieving invoices data from: {base_url}")
        print(f"INFO: Page size: {page_size}")
        print(" Fetching all invoices using pagination...")
        print("-" * 60)
        
        while page <= 10:  # Continue until no more pages or max pages reached
            # Get headers with valid token (only refresh if expired)
            fresh_headers = get_fresh_api_headers(tenant_id, app_key)
            if not fresh_headers:
                print(f" Failed to get fresh headers for invoices page {page}")
                return None
            
            # Add pagination parameters
            params = {
                "page": page,
                "pageSize": page_size
            }
            
            print(f" Fetching invoices page {page}...")
            response, success = make_api_request_with_retry(base_url, fresh_headers, params)
            
            if not success or not response:
                print(f" Failed to make API request for invoices page {page}")
                return None
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                json_response = response.json()
                invoices_data = json_response.get('data', [])
                pagination = json_response.get('pagination', {})
                
                # Process each invoice as they are fetched
                invoice_count = len(invoices_data)
                has_more = pagination.get('hasMore', False)
                
                print(f" Page {page}: Retrieved {invoice_count} invoices")
                
                # Process each invoice and extract only the required fields
                for invoice in invoices_data:
                    # Extract only the fields we need
                    reference_number = invoice.get('referenceNumber', '')
                    invoice_date = invoice.get('invoiceDate', '')
                    # Extract customer ID
                    customer = invoice.get('customer', {})
                    customer_id = customer.get('id') if isinstance(customer, dict) else None
                    
                    # Create simplified invoice record with only the required fields
                    invoice_record = {
                        'referenceNumber': reference_number,
                        'invoice_date': invoice_date,
                        'customer_id': customer_id
                    }
                    
                    # Store the simplified invoice data
                    invoices.append(invoice_record)
                    
                    total_invoices_processed += 1
                
                print(f" Page {page}: Added {invoice_count} invoices (Total: {total_invoices_processed})")
                
                # Check if there are more pages
                if invoice_count == 0:
                    print(f" No invoices returned on page {page}. Fetch complete!")
                    break
                elif invoice_count < page_size:
                    print(f" Partial page ({invoice_count} invoices). Reached end of data!")
                    break
                elif 'hasMore' in pagination and not has_more:
                    print(f" API indicates no more pages (hasMore=False). Fetch complete!")
                    break
                else:
                    # Continue to next page
                    print(f" Full page retrieved ({page_size} invoices). Continuing to next page...")
                
                # Increment page counter
                page += 1
                
                # Safety check to prevent infinite loops
                if page > 10:
                    print(f" Reached maximum page limit ({max_pages}). Stopping pagination.")
                    break
                
            else:
                if response.status_code == 404:
                    print(f" Page {page} not found - reached end of data. Fetch complete!")
                    break
                else:
                    print(f" Error retrieving invoices on page {page}: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
        
        # Print final summary
        print(f"\n Invoices Fetch Summary:")
        print(f"  - Total invoices processed: {total_invoices_processed}")
        print(f"  - Pages processed: {page}")
        print(f"  - Invoices stored in local array: {len(invoices)}")
        
        # Return success status and summary
        result = {
            "summary": {
                "total_processed": total_invoices_processed,
                "pages_processed": page,
                "invoices_stored": len(invoices)
            },
            "success": total_invoices_processed > 0
        }
        
        print(f" SUCCESS! Fetched {total_invoices_processed} invoices and stored {len(invoices)} in local array")
        return result
                     
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return None


def get_memberships(tenant_id, app_key=None, page_size=200):
    """
    Fetch all memberships from ServiceTitan API and store in local memberships array
    API endpoint: https://api.servicetitan.io/memberships/v2/tenant/{tenant_id}/memberships
    Extracts only customerId and membershipTypeId
    Returns: success status and summary
    """
    
    print("MEMBERSHIPS: Fetching memberships and storing in local array...")
    print("-" * 60)
    
    # Clear the local memberships array before fetching new data
    global memberships
    memberships.clear()
    
    # API endpoint for memberships
    base_url = f"https://api.servicetitan.io/memberships/v2/tenant/{tenant_id}/memberships"
    
    # Get a valid token
    valid_token = get_valid_token()
    if not valid_token:
        print(" Failed to get valid token for memberships fetching")
        return None
    
    # Headers with authorization
    headers = get_api_headers(tenant_id, app_key)
    if not headers:
        return None
    
    # Initialize counters
    total_memberships_processed = 0
    page = 1
    
    try:
        print(f" Retrieving memberships data from: {base_url}")
        print(f"INFO: Page size: {page_size}")
        print(" Fetching all memberships using pagination...")
        print("-" * 60)
        
        while page <= 10:  # Continue until no more pages or max pages reached
            # Get headers with valid token (only refresh if expired)
            fresh_headers = get_fresh_api_headers(tenant_id, app_key)
            if not fresh_headers:
                print(f" Failed to get fresh headers for memberships page {page}")
                return None
            
            # Add pagination parameters
            params = {
                "page": page,
                "pageSize": page_size
            }
            
            print(f" Fetching memberships page {page}...")
            response, success = make_api_request_with_retry(base_url, fresh_headers, params)
            
            if not success or not response:
                print(f" Failed to make API request for memberships page {page}")
                return None
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                json_response = response.json()
                memberships_data = json_response.get('data', [])
                pagination = json_response.get('pagination', {})
                
                # Process each membership as they are fetched
                membership_count = len(memberships_data)
                has_more = pagination.get('hasMore', False)
                
                print(f" Page {page}: Retrieved {membership_count} memberships")
                
                # Process each membership and extract only the required fields
                for membership in memberships_data:
                    # Extract only the fields we need
                    customer_id = membership.get('customerId')
                    membership_type_id = membership.get('membershipTypeId')
                    


                    # Create simplified membership record with only the required fields
                    membership_record = {
                        'customerId': customer_id,
                        'membershipTypeId': membership_type_id
                    }
                    
                    # Store the simplified membership data
                    memberships.append(membership_record)
                    total_memberships_processed += 1
                
                print(f" Page {page}: Added {membership_count} memberships (Total: {total_memberships_processed})")
                
                # Check if there are more pages
                if membership_count == 0:
                    print(f" No memberships returned on page {page}. Fetch complete!")
                    break
                elif membership_count < page_size:
                    print(f" Partial page ({membership_count} memberships). Reached end of data!")
                    break
                elif 'hasMore' in pagination and not has_more:
                    print(f" API indicates no more pages (hasMore=False). Fetch complete!")
                    break
                else:
                    # Continue to next page
                    print(f" Full page retrieved ({page_size} memberships). Continuing to next page...")
                
                # Increment page counter
                page += 1
                
                # Safety check to prevent infinite loops
                if page > 10:
                    print(f" Reached maximum page limit ({max_pages}). Stopping pagination.")
                    break
                
            else:
                if response.status_code == 404:
                    print(f" Page {page} not found - reached end of data. Fetch complete!")
                    break
                else:
                    print(f" Error retrieving memberships on page {page}: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
        
        # Print final summary
        print(f"\n Memberships Fetch Summary:")
        print(f"  - Total memberships processed: {total_memberships_processed}")
        print(f"  - Pages processed: {page}")
        print(f"  - Memberships stored in local array: {len(memberships)}")
        
        # Return success status and summary
        result = {
            "summary": {
                "total_processed": total_memberships_processed,
                "pages_processed": page,
                "memberships_stored": len(memberships)
            },
            "success": total_memberships_processed > 0
        }
        
        print(f" SUCCESS! Fetched {total_memberships_processed} memberships and stored {len(memberships)} in local array")
        return result
                     
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return None


def get_jobs(tenant_id, app_key=None, page_size=200):
    """
    Fetch jobs from ServiceTitan API using pagination and store in local jobs array
    API endpoint: https://api.servicetitan.io/jpm/v2/tenant/{tenant_id}/jobs
    Extracts only customerId and businessUnitId
    Uses pagination instead of individual customer requests for better performance
    Returns: success status and summary
    """
    
    print("JOBS: Fetching jobs using pagination and storing in local array...")
    print("-" * 60)
    
    # Clear the local jobs array before fetching new data
    global jobs
    jobs.clear()
    
    # API endpoint for jobs
    base_url = f"https://api.servicetitan.io/jpm/v2/tenant/{tenant_id}/jobs"
    
    # Get a valid token
    valid_token = get_valid_token()
    if not valid_token:
        print(" Failed to get valid token for jobs fetching")
        return None
    
    # Headers with authorization
    headers = get_api_headers(tenant_id, app_key)
    if not headers:
        return None
    
    # Initialize counters
    total_jobs_processed = 0
    page = 1
    
    try:
        print(f" Retrieving jobs data from: {base_url}")
        print(f"INFO: Page size: {page_size}")
        print(" Fetching all jobs using pagination...")
        print("-" * 60)
        
        while page <= 10:  # Continue until no more pages or max pages reached
            # Get headers with valid token (only refresh if expired)
            fresh_headers = get_fresh_api_headers(tenant_id, app_key)
            if not fresh_headers:
                print(f" Failed to get fresh headers for jobs page {page}")
                return None
            
            # Add pagination parameters
            params = {
                "page": page,
                "pageSize": page_size
            }
            
            print(f" Fetching jobs page {page}...")
            response, success = make_api_request_with_retry(base_url, fresh_headers, params)
            
            if not success or not response:
                print(f" Failed to make API request for jobs page {page}")
                return None
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                json_response = response.json()
                jobs_data = json_response.get('data', [])
                pagination = json_response.get('pagination', {})
                
                # Process each job as they are fetched
                job_count = len(jobs_data)
                has_more = pagination.get('hasMore', False)
                
                print(f" Page {page}: Retrieved {job_count} jobs")
                
                # Process each job and extract only the required fields
                for job in jobs_data:
                    # Extract only the fields we need
                    job_customer_id = job.get('customerId')
                    job_business_unit_id = job.get('businessUnitId')
                    
                    # Create simplified job record with only the required fields
                    job_record = {
                        'customerId': job_customer_id,
                        'businessUnitId': job_business_unit_id
                    }
                    
                    # Store the simplified job data
                    jobs.append(job_record)
                    total_jobs_processed += 1
                
                print(f" Page {page}: Added {job_count} jobs (Total: {total_jobs_processed})")
                
                # Check if there are more pages
                if job_count == 0:
                    print(f" No jobs returned on page {page}. Fetch complete!")
                    break
                elif job_count < page_size:
                    print(f" Partial page ({job_count} jobs). Reached end of data!")
                    break
                elif 'hasMore' in pagination and not has_more:
                    print(f" API indicates no more pages (hasMore=False). Fetch complete!")
                    break
                else:
                    # Continue to next page
                    print(f" Full page retrieved ({page_size} jobs). Continuing to next page...")
                
                # Increment page counter
                page += 1
                
                # Safety check to prevent infinite loops
                if page > 10:
                    print(f" Reached maximum page limit ({max_pages}). Stopping pagination.")
                    break
                
            else:
                if response.status_code == 404:
                    print(f" Page {page} not found - reached end of data. Fetch complete!")
                    break
                else:
                    print(f" Error retrieving jobs on page {page}: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
        
        # Calculate summary statistics
        customers_with_jobs = set()
        for job in jobs:
            customer_id = job.get('customerId')
            if customer_id:
                customers_with_jobs.add(customer_id)
        
        # Print final summary
        print(f"\n Jobs Fetch Summary:")
        print(f"  - Total jobs processed: {total_jobs_processed}")
        print(f"  - Pages processed: {page}")
        print(f"  - Jobs stored in local array: {len(jobs)}")
        print(f"  - Unique customers with jobs: {len(customers_with_jobs)}")
        
        # Return success status and summary
        result = {
            "summary": {
                "total_processed": total_jobs_processed,
                "pages_processed": page,
                "jobs_stored": len(jobs),
                "customers_with_jobs": len(customers_with_jobs)
            },
            "success": total_jobs_processed > 0
        }
        
        print(f" SUCCESS! Fetched {total_jobs_processed} jobs and stored {len(jobs)} in local array")
        return result
                     
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return None


def get_business_units(tenant_id, app_key=None, page_size=200):
    """
    Fetch all business units from ServiceTitan API and store in local business_units array
    API endpoint: https://api.servicetitan.io/jpm/v2/tenant/{tenant_id}/business-units
    Extracts only id and name as pairs
    Returns: success status and summary
    """
    
    print("BUSINESS_UNITS: Fetching business units and storing in local array...")
    print("-" * 60)
    
    # Clear the local business_units array before fetching new data
    global business_units
    business_units.clear()

    # API endpoint for business units
    base_url = f"https://api.servicetitan.io/settings/v2/tenant/{tenant_id}/business-units"
    
    # Get a valid token
    valid_token = get_valid_token()
    if not valid_token:
        print(" Failed to get valid token for business units fetching")
        return None
    
    # Headers with authorization
    headers = get_api_headers(tenant_id, app_key)
    if not headers:
        return None
    
    # Initialize counters
    total_business_units_processed = 0
    page = 1
    
    try:
        print(f" Retrieving business units data from: {base_url}")
        print(f"INFO: Page size: {page_size}")
        print(" Fetching all business units using pagination...")
        print("-" * 60)
        
        while page <= 10:  # Continue until no more pages or max pages reached
            # Get headers with valid token (only refresh if expired)
            fresh_headers = get_fresh_api_headers(tenant_id, app_key)
            if not fresh_headers:
                print(f" Failed to get fresh headers for business units page {page}")
                return None
            
            # Add pagination parameters
            params = {
                "page": page,
                "pageSize": page_size
            }
            
            print(f" Fetching business units page {page}...")
            response, success = make_api_request_with_retry(base_url, fresh_headers, params)
            
            if not success or not response:
                print(f" Failed to make API request for business units page {page}")
                return None
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                json_response = response.json()
                business_units_data = json_response.get('data', [])
                pagination = json_response.get('pagination', {})
                
                # Process each job type as they are fetched
                business_unit_count = len(business_units_data)
                has_more = pagination.get('hasMore', False)
                
                print(f" Page {page}: Retrieved {business_unit_count} business units")
                
                # Process each job type and extract only the required fields
                for business_unit in business_units_data:
                    # Extract only the fields we need
                    business_unit_id = business_unit.get('id')
                    business_unit_name = business_unit.get('name')
                    
                    # Create simplified job type record with only the required fields
                    business_unit_record = {
                        'id': business_unit_id,
                        'name': business_unit_name
                    }
                    
                    # Store the simplified job type data
                    business_units.append(business_unit_record)
                    total_business_units_processed += 1
                
                print(f" Page {page}: Added {business_unit_count} business units (Total: {total_business_units_processed})")
                
                # Check if there are more pages
                if business_unit_count == 0:
                    print(f" No business units returned on page {page}. Fetch complete!")
                    break
                elif business_unit_count < page_size:
                    print(f" Partial page ({business_unit_count} business units). Reached end of data!")
                    break
                elif 'hasMore' in pagination and not has_more:
                    print(f" API indicates no more pages (hasMore=False). Fetch complete!")
                    break
                else:
                    # Continue to next page
                    print(f" Full page retrieved ({page_size} business units). Continuing to next page...")
                
                # Increment page counter
                page += 1
                
                # Safety check to prevent infinite loops
                if page > 10:
                    print(f" Reached maximum page limit ({max_pages}). Stopping pagination.")
                    break
                
            else:
                if response.status_code == 404:
                    print(f" Page {page} not found - reached end of data. Fetch complete!")
                    break
                else:
                    print(f" Error retrieving business units on page {page}: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
        
        # Print final summary
        print(f"\n Business Units Fetch Summary:")
        print(f"  - Total business units processed: {total_business_units_processed}")
        print(f"  - Pages processed: {page}")
        print(f"  - Business units stored in local array: {len(business_units)}")
        
        # Return success status and summary
        result = {
            "summary": {
                "total_processed": total_business_units_processed,
                "pages_processed": page,
                "business_units_stored": len(business_units)
            },
            "success": total_business_units_processed > 0
        }
        
        print(f" SUCCESS! Fetched {total_business_units_processed} business units and stored {len(business_units)} in local array")
        return result
                     
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error making request: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return None


def add_phone_numbers_to_customer_records():
    """
    Match contact data from contacts array to customer records in global_customer_data_array
    Adds phone_number and email fields to each customer record based on customer_id matching
    """
    print("CONTACTS: Adding phone numbers and emails to customer records...")
    print("-" * 60)
        
    # Get contacts data
    contacts_data = get_contacts_data()
    if not contacts_data:
        print(" No contacts data available for phone number matching")
        return
    
    # Get global customer data
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return
    
    print(f"PROCESS: Processing {len(global_customer_data_array)} customers with {len(contacts_data)} contacts")
    
    # Debug: Show contact types found
    contact_types = {}
    for contact in contacts_data:
        contact_type = contact.get('type', 'Unknown')
        contact_types[contact_type] = contact_types.get(contact_type, 0) + 1
    
    print(f"DEBUG: Contact types found: {contact_types}")
    
    # Create lookup dictionaries for phone numbers and emails by customer_id
    phone_numbers_by_customer = {}
    emails_by_customer = {}
    for contact in contacts_data:
        customer_id = contact.get('customerId')
        phone_number = contact.get('phoneNumber', '')
        email = contact.get('email', '')
        contact_type = contact.get('type', '')
        
        if customer_id and phone_number:
            # Collect ALL phone numbers for each customer
            if customer_id not in phone_numbers_by_customer:
                phone_numbers_by_customer[customer_id] = []
            phone_numbers_by_customer[customer_id].append(phone_number)
        
        # Collect ALL emails for each customer (regardless of type)
        if customer_id and email:
            if customer_id not in emails_by_customer:
                emails_by_customer[customer_id] = []
            emails_by_customer[customer_id].append({
                'email': email,
                'type': contact_type
            })
    
    # Add phone numbers and emails to each customer in global array
    customers_with_phone_numbers = 0
    customers_without_phone_numbers = 0
    customers_with_emails = 0
    customers_without_emails = 0
    
    for customer in global_customer_data_array:
        customer_id = customer.get('customer_id')
        if customer_id:
            # Get phone numbers and emails for this customer
            phone_numbers_list = phone_numbers_by_customer.get(customer_id, [])
            emails_list = emails_by_customer.get(customer_id, [])
            
            # Add phone numbers and emails to customer record
            customer['phone_numbers'] = phone_numbers_list  # List of all phone numbers
            customer['phone_number'] = phone_numbers_list[0] if phone_numbers_list else ''  # First phone number for backward compatibility
            customer['emails'] = emails_list  # List of all emails with types
            customer['email'] = emails_list[0]['email'] if emails_list else ''  # First email for backward compatibility
            
            if phone_numbers_list:
                customers_with_phone_numbers += 1
            else:
                customers_without_phone_numbers += 1
                
            if emails_list:
                customers_with_emails += 1
            else:
                customers_without_emails += 1
    
    # Calculate additional statistics for multiple phone numbers and emails
    total_phone_numbers = sum(len(phone_list) for phone_list in phone_numbers_by_customer.values())
    customers_with_multiple_phones = sum(1 for phone_list in phone_numbers_by_customer.values() if len(phone_list) > 1)
    total_emails = sum(len(email_list) for email_list in emails_by_customer.values())
    customers_with_multiple_emails = sum(1 for email_list in emails_by_customer.values() if len(email_list) > 1)
    
    print(f"\nSTATS: Contact Information Summary:")
    print(f"  - Total customers processed: {len(global_customer_data_array)}")
    print(f"  - Customers with phone numbers: {customers_with_phone_numbers}")
    print(f"  - Customers without phone numbers: {customers_without_phone_numbers}")
    print(f"  - Customers with multiple phone numbers: {customers_with_multiple_phones}")
    print(f"  - Total phone numbers collected: {total_phone_numbers}")
    print(f"  - Customers with emails: {customers_with_emails}")
    print(f"  - Customers without emails: {customers_without_emails}")
    print(f"  - Customers with multiple emails: {customers_with_multiple_emails}")
    print(f"  - Total emails collected: {total_emails}")
    print(f"  - Phone numbers available in contacts: {len(phone_numbers_by_customer)}")
    print(f"  - Emails available in contacts: {len(emails_by_customer)}")
    
    print(f"SUCCESS: Added phone numbers to {customers_with_phone_numbers} customers")
    print(f"SUCCESS: Added emails to {customers_with_emails} customers")
    print(f"SUCCESS: Collected {total_phone_numbers} total phone numbers from {customers_with_phone_numbers} customers")
    print(f"SUCCESS: Collected {total_emails} total emails from {customers_with_emails} customers")


def add_location_data_to_customer_records():
    """
    Match location data from locations array to customer records in global_customer_data_array
    Adds location_address and location_name fields to each customer record based on customer_id matching
    """
    print("Adding location data to customer records...")
    print("-" * 60)
        
    # Get locations data
    locations_data = get_locations_data()
    if not locations_data:
        print("WARNING: No locations data available for location data matching")
        return
    
    # Get global customer data
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return
    
    print(f" Processing {len(global_customer_data_array)} customers with {len(locations_data)} locations")
    
    
    # Create a lookup dictionary for locations by customer_id
    # Group all locations by customer_id first
    locations_by_customer_temp = {}
    for location in locations_data:
        customer_id = location.get('customerId')
        if customer_id:
            if customer_id not in locations_by_customer_temp:
                locations_by_customer_temp[customer_id] = []
            locations_by_customer_temp[customer_id].append(location)
    
    # Collect ALL addresses for each customer
    locations_by_customer = {}
    for customer_id, customer_locations in locations_by_customer_temp.items():
        # Collect all addresses for this customer
        all_addresses = []
        latest_location = None
        latest_date = None
        
        for location in customer_locations:
            location_name = location.get('name', '')
            location_address = location.get('address', {})
            created_on = location.get('createdOn', '')
            modified_on = location.get('modifiedOn', '')
            
            # Extract address components
            address_info = {
                'name': location_name,
                'street': location_address.get('street', '') if isinstance(location_address, dict) else '',
                'city': location_address.get('city', '') if isinstance(location_address, dict) else '',
                'zip': location_address.get('zip', '') if isinstance(location_address, dict) else '',
                'address': location_address,  # Full address object
                'createdOn': created_on,
                'modifiedOn': modified_on
            }
            
            all_addresses.append(address_info)
            
            # Also find the latest location for backward compatibility
            location_date = modified_on or created_on
            if location_date:
                try:
                    from datetime import datetime
                    if isinstance(location_date, str):
                        date_obj = datetime.fromisoformat(location_date.replace('Z', '+00:00'))
                    else:
                        date_obj = location_date
                    
                    if latest_date is None or date_obj > latest_date:
                        latest_date = date_obj
                        latest_location = address_info
                except (ValueError, TypeError):
                    if latest_location is None:
                        latest_location = address_info
            else:
                if latest_location is None:
                    latest_location = address_info
        
        # Store all addresses and latest location info
        locations_by_customer[customer_id] = {
            'all_addresses': all_addresses,
            'latest_location': latest_location
        }
        
        total_locations = len(customer_locations)
        if total_locations > 1:
            print(f"Customer {customer_id}: Collected {total_locations} addresses")
        else:
            print(f"Customer {customer_id}: Collected 1 address")
    
    # Add location data to each customer in global array
    customers_with_locations = 0
    customers_without_locations = 0
    
    for customer in global_customer_data_array:
        customer_id = customer.get('customer_id')
        if customer_id:
            # Get location data for this customer
            location_data = locations_by_customer.get(customer_id, {})
            
            # Add all addresses to customer record
            all_addresses = location_data.get('all_addresses', [])
            latest_location = location_data.get('latest_location', {})
            
            customer['addresses'] = all_addresses  # All addresses for this customer
            
            # For backward compatibility, also add the latest location data
            if latest_location:
                customer['location_name'] = latest_location.get('name', '')
                customer['location_address'] = latest_location.get('address', {})
                customer['location_street'] = latest_location.get('street', '')
                customer['location_city'] = latest_location.get('city', '')
                customer['location_number'] = latest_location.get('zip', '')  # zip -> location_number
            else:
                customer['location_name'] = ''
                customer['location_address'] = {}
                customer['location_street'] = ''
                customer['location_city'] = ''
                customer['location_number'] = ''
            
            if all_addresses:
                customers_with_locations += 1
            else:
                customers_without_locations += 1
    
    # Calculate additional statistics for multiple addresses
    total_addresses = sum(len(location_data.get('all_addresses', [])) for location_data in locations_by_customer.values())
    customers_with_multiple_addresses = sum(1 for location_data in locations_by_customer.values() if len(location_data.get('all_addresses', [])) > 1)
    
    print(f"\n Location Data Summary:")
    print(f"  - Total customers processed: {len(global_customer_data_array)}")
    print(f"  - Customers with location data: {customers_with_locations}")
    print(f"  - Customers without location data: {customers_without_locations}")
    print(f"  - Customers with multiple addresses: {customers_with_multiple_addresses}")
    print(f"  - Total addresses collected: {total_addresses}")
    print(f"  - Locations available in data: {len(locations_by_customer)}")
    
    print(f" SUCCESS! Added location data to {customers_with_locations} customers")
    print(f" SUCCESS! Collected {total_addresses} total addresses from {customers_with_locations} customers")




def add_invoice_numbers_to_customer_records():
    """
    Match invoice reference numbers from invoices array to customer records in global_customer_data_array
    Adds invoice_numbers field to each customer record based on customer_id matching
    """
    print(" Adding invoice numbers to customer records...")
    print("-" * 60)
    
    # Get invoices data
    invoices_data = get_invoices_data()
    if not invoices_data:
        print(" No invoices data available for invoice number matching")
        return
    
    # Get global customer data
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return
    
    print(f" Processing {len(global_customer_data_array)} customers with {len(invoices_data)} invoices")
    
    # Process customers in batches of 100
    batch_size = 100
    total_customers_processed = 0
    customers_with_invoices = 0
    customers_without_invoices = 0
    
    # Time-based early exit for very large datasets
    start_time = time.time()
    max_processing_time = 1800  # 30 minutes max for this function
    
    for batch_start in range(0, len(global_customer_data_array), batch_size):
        batch_end = min(batch_start + batch_size, len(global_customer_data_array))
        batch_customers = global_customer_data_array[batch_start:batch_end]
        batch_number = (batch_start // batch_size) + 1
        total_batches = (len(global_customer_data_array) + batch_size - 1) // batch_size
        
        # Get customer IDs for this batch
        batch_customer_ids = [customer.get('customer_id') for customer in batch_customers if customer.get('customer_id')]
        
        # Only show batch progress every 10 batches to reduce log verbosity
        if batch_number % 10 == 1 or batch_number == total_batches:
            print(f" Processing batch {batch_number}/{total_batches} ({len(batch_customers)} customers)")
        
        # Create a lookup for invoice reference numbers by customer ID for this batch only
        invoice_numbers_by_customer = {}
        for invoice in invoices_data:
            customer_id = invoice.get('customer_id')
            reference_number = invoice.get('referenceNumber', '')
            invoice_date = invoice.get('invoice_date', '')
            # Only process invoices for customers in this batch
            # Skip invoices where invoice_date is null
            if customer_id in batch_customer_ids and reference_number and invoice_date is not None:
                if customer_id not in invoice_numbers_by_customer:
                    invoice_numbers_by_customer[customer_id] = []
                invoice_numbers_by_customer[customer_id].append(reference_number)
                invoice_numbers_by_customer[customer_id].append(invoice_date)
        
        # Only show batch summary every 10 batches
        if batch_number % 10 == 1 or batch_number == total_batches:
            print(f" Batch {batch_number}: Found invoice numbers for {len(invoice_numbers_by_customer)} customers")
        
        for customer in batch_customers:
            customer_id = customer.get('customer_id')
            if customer_id:
                # Get invoice numbers for this customer from batch lookup
                invoice_numbers = invoice_numbers_by_customer.get(customer_id, [])
                
                # Separate reference numbers and invoice dates
                billingname = []  # reference numbers
                billingline1 = []  # invoice dates
                
                # Process pairs: [ref_num, date, ref_num, date, ...]
                for i in range(0, len(invoice_numbers), 2):
                    if i + 1 < len(invoice_numbers):
                        reference_number = invoice_numbers[i]
                        invoice_date = invoice_numbers[i + 1]
                        billingname.append(reference_number)
                        billingline1.append(invoice_date)
                
                # Add separate fields to customer record
                customer['billingname'] = billingname
                customer['billingline1'] = billingline1
                
                if invoice_numbers:
                    customers_with_invoices += 1
                else:
                    customers_without_invoices += 1
                
                total_customers_processed += 1
        
        # Only show batch completion every 10 batches
        if batch_number % 10 == 1 or batch_number == total_batches:
            print(f" Batch {batch_number}: Processed {len(batch_customers)} customers")
        
        # Check for time-based early exit
        elapsed_time = time.time() - start_time
        if elapsed_time > max_processing_time:
            print(f" Time limit reached ({max_processing_time}s). Stopping invoice processing early.")
            print(f" Processed {total_customers_processed} customers in {elapsed_time:.1f} seconds")
            break
    
    print(f"\n Invoice Numbers Summary:")
    print(f"  - Total customers processed: {total_customers_processed}")
    print(f"  - Customers with invoice numbers: {customers_with_invoices}")
    print(f"  - Customers without invoice numbers: {customers_without_invoices}")
    print(f"  - Total invoices available: {len(invoices_data)}")
    print(f"  - Batches processed: {total_batches}")
    
    print(f"SUCCESS: Created billingname and billingline1 fields for {customers_with_invoices} customers")
    


def add_membership_vip_status_to_customer_records():
    """
    Match membership data with customer records and add is_vip field
    If customer has membershipTypeId, is_vip = "YES", otherwise is_vip = "NO"
    """
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return
    
    memberships_data = get_memberships_data()
    if not memberships_data:
        print(" No membership data available")
        return
    
    print(" Adding VIP status based on membership data to customer records...")
    print("-" * 60)
    
    print(f" Processing {len(global_customer_data_array)} customers with {len(memberships_data)} memberships")
    
    # Create a lookup for membership type IDs by customer ID
    membership_type_ids_by_customer = {}
    for membership in memberships_data:
        customer_id = membership.get('customerId')
        membership_type_id = membership.get('membershipTypeId')
        
        if customer_id and membership_type_id:
            membership_type_ids_by_customer[customer_id] = membership_type_id
    
    print(f" Found membership type IDs for {len(membership_type_ids_by_customer)} customers")
    
    # Process customers in batches of 100
    batch_size = 100
    total_customers_processed = 0
    customers_with_membership = 0
    customers_without_membership = 0
    
    # Time-based early exit for very large datasets
    start_time = time.time()
    max_processing_time = 1800  # 30 minutes max for this function
    
    for batch_start in range(0, len(global_customer_data_array), batch_size):
        batch_end = min(batch_start + batch_size, len(global_customer_data_array))
        batch_customers = global_customer_data_array[batch_start:batch_end]
        batch_number = (batch_start // batch_size) + 1
        total_batches = (len(global_customer_data_array) + batch_size - 1) // batch_size
        
        # Get customer IDs for this batch
        batch_customer_ids = [customer.get('customer_id') for customer in batch_customers if customer.get('customer_id')]
        
        # Only show batch progress every 10 batches to reduce log verbosity
        if batch_number % 10 == 1 or batch_number == total_batches:
            print(f" Processing batch {batch_number}/{total_batches} ({len(batch_customers)} customers)")
        
        # Create a lookup for membership type IDs by customer ID for this batch only
        batch_membership_type_ids = {}
        for customer_id in batch_customer_ids:
            if customer_id in membership_type_ids_by_customer:
                batch_membership_type_ids[customer_id] = membership_type_ids_by_customer[customer_id]
        
        # Only show batch summary every 10 batches
        if batch_number % 10 == 1 or batch_number == total_batches:
            print(f" Batch {batch_number}: Found membership type IDs for {len(batch_membership_type_ids)} customers")
        
        for customer in batch_customers:
            customer_id = customer.get('customer_id')
            if customer_id:
                # Check if customer has membership type ID
                membership_type_id = batch_membership_type_ids.get(customer_id)
                
                # Set is_vip field based on membership existence
                if membership_type_id:
                    customer['is_vip'] = "YES"
                    customer['membership_type_id'] = membership_type_id
                    customers_with_membership += 1
                else:
                    customer['is_vip'] = "NO"
                    customer['membership_type_id'] = None
                    customers_without_membership += 1
                
                
                total_customers_processed += 1
        
        # Only show batch completion every 10 batches
        if batch_number % 10 == 1 or batch_number == total_batches:
            print(f" Batch {batch_number}: Processed {len(batch_customers)} customers")
        
        # Check for time-based early exit
        elapsed_time = time.time() - start_time
        if elapsed_time > max_processing_time:
            print(f" Time limit reached ({max_processing_time}s). Stopping VIP status processing early.")
            print(f" Processed {total_customers_processed} customers in {elapsed_time:.1f} seconds")
            break
    
    print(f"\n VIP Status Summary:")
    print(f"  - Total customers processed: {total_customers_processed}")
    print(f"  - Customers with membership (VIP=YES): {customers_with_membership}")
    print(f"  - Customers without membership (VIP=NO): {customers_without_membership}")
    print(f"  - Total memberships available: {len(memberships_data)}")
    print(f"  - Batches processed: {total_batches}")
    
    # Show sample of customers with VIP status (reduced verbosity)
    print(f"\n Sample customers with VIP status:")
    sample_count = min(2, len(global_customer_data_array))
    for i in range(sample_count):
        customer = global_customer_data_array[i]
        customer_id = customer.get('customer_id')
        is_vip = customer.get('is_vip', 'NOT_FOUND')
        print(f"  - Customer {customer_id}: is_vip={is_vip}")
    
    print(f" SUCCESS! Added VIP status to {total_customers_processed} customers")
    print(f" Final VIP status summary: {customers_with_membership} VIP customers, {customers_without_membership} non-VIP customers")


def add_latest_business_unit_names_to_customer_records():
    """
    Match job data with customer records and add business unit name to business_unit_name field
    For each customer, finds the latest job and saves the business unit name (not ID)
    If no jobs, saves "No Past Job"
    Processes customers in batches of 100
    """
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return
    
    jobs_data = get_jobs_data()
    if not jobs_data:
        print(" No jobs data available")
        return
    
    business_units_data = get_business_units_data()
    if not business_units_data:
        print(" No business units data available")
        return
    
    print(" Adding business unit names to customer records...")
    print("-" * 60)
    
    print(f" Processing {len(global_customer_data_array)} customers with {len(jobs_data)} jobs and {len(business_units_data)} business units")
    
    # Create a lookup for job type names by job type ID
    business_unit_names_by_id = {}
    for business_unit in business_units_data:
        business_unit_id = business_unit.get('id')
        business_unit_name = business_unit.get('name')
    
        if business_unit_id and business_unit_name:
            business_unit_names_by_id[business_unit_id] = business_unit_name
    
    print(f" Created lookup for {len(business_unit_names_by_id)} business unit names")
    
    # Create a lookup for the latest job data by customer ID
    # We need to find the latest job for each customer
    latest_job_data_by_customer = {}
    for job in jobs_data:
        customer_id = job.get('customerId')
        business_unit_id = job.get('businessUnitId')
        if customer_id and business_unit_id:
            # For now, we'll just take the last job data we encounter for each customer
            # In a real scenario, you might want to sort by date or job ID to get the truly latest job
            latest_job_data_by_customer[customer_id] = {
                'businessUnitId': business_unit_id
            }
    print(f"latest job data by customer: {latest_job_data_by_customer}")
    print(f" Found latest job data for {len(latest_job_data_by_customer)} customers")
    
    # Process customers in batches of 100
    batch_size = 100
    total_customers_processed = 0
    customers_with_jobs = 0
    customers_without_jobs = 0
    
    # Time-based early exit for very large datasets
    start_time = time.time()
    max_processing_time = 1800  # 30 minutes max for this function
    
    for batch_start in range(0, len(global_customer_data_array), batch_size):
        batch_end = min(batch_start + batch_size, len(global_customer_data_array))
        batch_customers = global_customer_data_array[batch_start:batch_end]
        batch_number = (batch_start // batch_size) + 1
        total_batches = (len(global_customer_data_array) + batch_size - 1) // batch_size
        
        # Get customer IDs for this batch
        batch_customer_ids = [customer.get('customer_id') for customer in batch_customers if customer.get('customer_id')]
        
        # Only show batch progress every 10 batches to reduce log verbosity
        if batch_number % 10 == 1 or batch_number == total_batches:
            print(f" Processing batch {batch_number}/{total_batches} ({len(batch_customers)} customers)")
        
        # Create a lookup for latest job data by customer ID for this batch only
        batch_latest_job_data = {}
        for customer_id in batch_customer_ids:
            if customer_id in latest_job_data_by_customer:
                batch_latest_job_data[customer_id] = latest_job_data_by_customer[customer_id]
        
        # Only show batch summary every 10 batches
        if batch_number % 10 == 1 or batch_number == total_batches:
            print(f" Batch {batch_number}: Found latest job data for {len(batch_latest_job_data)} customers")
        
        for customer in batch_customers:
            customer_id = customer.get('customer_id')
            if customer_id:
                # Check if customer has latest job data
                latest_job_data = batch_latest_job_data.get(customer_id)
                
                # Set business_unit_name field based on latest job
                if latest_job_data:
                    customers_with_jobs += 1
                    latest_business_unit_id = latest_job_data.get('businessUnitId')
                    
                    latest_business_unit_name = business_unit_names_by_id.get(latest_business_unit_id)
                    if latest_business_unit_name:
                        customer['business_unit_name'] = latest_business_unit_name
                    else:
                        customer['business_unit_name'] = "Unknown Business Unit"
                else:
                    # No jobs found - save "No Past Job"
                    customer['business_unit_name'] = "No Past Job"
                    customers_without_jobs += 1
                
                
                total_customers_processed += 1
        
        # Only show batch completion every 10 batches
        if batch_number % 10 == 1 or batch_number == total_batches:
            print(f" Batch {batch_number}: Processed {len(batch_customers)} customers")
        
        # Check for time-based early exit
        elapsed_time = time.time() - start_time
        if elapsed_time > max_processing_time:
            print(f" Time limit reached ({max_processing_time}s). Stopping business unit processing early.")
            print(f" Processed {total_customers_processed} customers in {elapsed_time:.1f} seconds")
            break
    
    print(f"\n Business Unit Names Summary:")
    print(f"  - Total customers processed: {total_customers_processed}")
    print(f"  - Customers with jobs: {customers_with_jobs}")
    print(f"  - Customers without jobs (No Past Job): {customers_without_jobs}")
    print(f"  - Total jobs available: {len(jobs_data)}")
    print(f"  - Total business units available: {len(business_units_data)}")
    print(f"  - Batches processed: {total_batches}")
    
    # Show sample of customers with business unit names (reduced verbosity)
    print(f"\n Sample customers with business_unit_name field:")
    sample_count = min(2, len(global_customer_data_array))
    for i in range(sample_count):
        customer = global_customer_data_array[i]
        customer_id = customer.get('customer_id')
        business_unit_name = customer.get('business_unit_name', 'NOT_FOUND')
        print(f"  - Customer {customer_id}: business_unit_name={business_unit_name}")
    
    print(f" SUCCESS! Added business unit names to {total_customers_processed} customers")
    print(f" Final job type names summary: {customers_with_jobs} customers with jobs, {customers_without_jobs} customers without jobs")


def get_customer_contact_and_address_data():
    """
    Extract all phone, email, street, city, zip values matched to customer_id
    Returns a list of dictionaries with customer_id and all contact/address information
    """
    print(" Extracting customer contact and address data...")
    print("-" * 60)
    
    # Get the global customer data array
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return []
    
    # Ensure we have the latest data by calling the functions that add contact and address data
    print(" Ensuring contact and address data is up to date...")
    add_phone_numbers_to_customer_records()
    add_location_data_to_customer_records()
    
    # Extract the required fields for each customer
    customer_contact_address_data = []
    
    for customer in global_customer_data_array:
        customer_id = customer.get('customer_id')
        if customer_id:
            # Extract contact information
            phone_numbers_list = customer.get('phone_numbers', [])
            phone = customer.get('phone_number', '')  # First phone number for backward compatibility
            emails_list = customer.get('emails', [])
            email = customer.get('email', '')  # First email for backward compatibility
            
            # Extract address information from location data
            all_addresses = customer.get('addresses', [])
            street = customer.get('location_street', '')
            city = customer.get('location_city', '')
            zip_code = customer.get('location_number', '')  # This is the zip field from location data
            
            # Also get customer address data (from customer record itself)
            customer_street = customer.get('customer_address_street', '')
            customer_city = customer.get('customer_address_city', '')
            
            # Create the consolidated record
            contact_address_record = {
                'customer_id': customer_id,
                'phone': phone,  # First phone number
                'phone_numbers': phone_numbers_list,  # All phone numbers
                'email': email,  # First email
                'emails': emails_list,  # All emails with types
                'street': street or customer_street,  # Use location street if available, fallback to customer street
                'city': city or customer_city,        # Use location city if available, fallback to customer city
                'zip': zip_code,
                'addresses': all_addresses  # All addresses for this customer
            }
            
            customer_contact_address_data.append(contact_address_record)
    
    print(f"\n Contact and Address Data Summary:")
    print(f"  - Total customers processed: {len(customer_contact_address_data)}")
    
    # Count customers with different types of data
    customers_with_phone = sum(1 for record in customer_contact_address_data if record['phone'])
    customers_with_multiple_phones = sum(1 for record in customer_contact_address_data if len(record['phone_numbers']) > 1)
    total_phone_numbers = sum(len(record['phone_numbers']) for record in customer_contact_address_data)
    customers_with_email = sum(1 for record in customer_contact_address_data if record['email'])
    customers_with_multiple_emails = sum(1 for record in customer_contact_address_data if len(record['emails']) > 1)
    total_emails = sum(len(record['emails']) for record in customer_contact_address_data)
    customers_with_addresses = sum(1 for record in customer_contact_address_data if record['addresses'])
    customers_with_multiple_addresses = sum(1 for record in customer_contact_address_data if len(record['addresses']) > 1)
    total_addresses = sum(len(record['addresses']) for record in customer_contact_address_data)
    customers_with_street = sum(1 for record in customer_contact_address_data if record['street'])
    customers_with_city = sum(1 for record in customer_contact_address_data if record['city'])
    customers_with_zip = sum(1 for record in customer_contact_address_data if record['zip'])
    
    print(f"  - Customers with phone numbers: {customers_with_phone}")
    print(f"  - Customers with multiple phone numbers: {customers_with_multiple_phones}")
    print(f"  - Total phone numbers collected: {total_phone_numbers}")
    print(f"  - Customers with email addresses: {customers_with_email}")
    print(f"  - Customers with multiple emails: {customers_with_multiple_emails}")
    print(f"  - Total emails collected: {total_emails}")
    print(f"  - Customers with addresses: {customers_with_addresses}")
    print(f"  - Customers with multiple addresses: {customers_with_multiple_addresses}")
    print(f"  - Total addresses collected: {total_addresses}")
    print(f"  - Customers with street addresses: {customers_with_street}")
    print(f"  - Customers with city information: {customers_with_city}")
    print(f"  - Customers with zip codes: {customers_with_zip}")
    
    # Show sample data
    print(f"\n Sample customer contact and address data:")
    sample_count = min(3, len(customer_contact_address_data))
    for i in range(sample_count):
        record = customer_contact_address_data[i]
        print(f"  - Customer {record['customer_id']}:")
        print(f"    Phone (first): {record['phone'] or 'N/A'}")
        print(f"    All phones: {record['phone_numbers'] or 'N/A'}")
        print(f"    Email (first): {record['email'] or 'N/A'}")
        print(f"    All emails: {record['emails'] or 'N/A'}")
        print(f"    Street: {record['street'] or 'N/A'}")
        print(f"    City: {record['city'] or 'N/A'}")
        print(f"    Zip: {record['zip'] or 'N/A'}")
        print(f"    Addresses: {len(record['addresses'])} address(es)")
        if record['addresses']:
            for j, address in enumerate(record['addresses'][:2]):  # Show first 2 addresses
                print(f"      Address {j+1}: {address.get('name', 'N/A')} - {address.get('street', 'N/A')}, {address.get('city', 'N/A')} {address.get('zip', 'N/A')}")
    
    print(f" SUCCESS! Extracted contact and address data for {len(customer_contact_address_data)} customers")
    return customer_contact_address_data


def export_customer_contact_address_to_csv(filename="customer_contact_address_data.csv"):
    """
    Export customer contact and address data to a CSV file
    """
    import csv
    
    print(f" Exporting customer contact and address data to {filename}...")
    
    # Get the contact and address data
    data = get_customer_contact_and_address_data()
    
    if not data:
        print(" No data to export")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['customer_id', 'phone', 'phone_numbers', 'email', 'emails', 'street', 'city', 'zip', 'addresses']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for record in data:
                # Convert lists to strings for CSV
                record_copy = record.copy()
                if 'phone_numbers' in record_copy and isinstance(record_copy['phone_numbers'], list):
                    record_copy['phone_numbers'] = '; '.join(record_copy['phone_numbers'])
                if 'emails' in record_copy and isinstance(record_copy['emails'], list):
                    # Convert email objects to strings
                    email_strings = []
                    for email_obj in record_copy['emails']:
                        if isinstance(email_obj, dict):
                            email_str = f"{email_obj.get('email', '')} ({email_obj.get('type', '')})"
                        else:
                            email_str = str(email_obj)
                        email_strings.append(email_str)
                    record_copy['emails'] = '; '.join(email_strings)
                if 'addresses' in record_copy and isinstance(record_copy['addresses'], list):
                    # Convert address objects to strings
                    address_strings = []
                    for address in record_copy['addresses']:
                        if isinstance(address, dict):
                            address_str = f"{address.get('name', '')} - {address.get('street', '')}, {address.get('city', '')} {address.get('zip', '')}"
                        else:
                            address_str = str(address)
                        address_strings.append(address_str)
                    record_copy['addresses'] = '; '.join(address_strings)
                writer.writerow(record_copy)
        
        print(f" Successfully exported {len(data)} records to {filename}")
        return True
        
    except Exception as e:
        print(f" Error exporting to CSV: {e}")
        return False


def get_all_phone_numbers_by_customer_id():
    """
    Get all phone numbers matched to customer_id
    Returns a dictionary with customer_id as key and list of phone numbers as value
    """
    print(" Extracting all phone numbers by customer ID...")
    print("-" * 60)
    
    # Get the global customer data array
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return {}
    
    # Ensure we have the latest contact data
    print(" Ensuring contact data is up to date...")
    add_phone_numbers_to_customer_records()
    
    # Create dictionary with customer_id as key and phone numbers list as value
    phone_numbers_by_customer = {}
    
    for customer in global_customer_data_array:
        customer_id = customer.get('customer_id')
        phone_numbers_list = customer.get('phone_numbers', [])
        
        if customer_id and phone_numbers_list:
            phone_numbers_by_customer[customer_id] = phone_numbers_list
    
    print(f"\n Phone Numbers Summary:")
    print(f"  - Total customers with phone numbers: {len(phone_numbers_by_customer)}")
    
    # Calculate statistics
    total_phone_numbers = sum(len(phone_list) for phone_list in phone_numbers_by_customer.values())
    customers_with_multiple_phones = sum(1 for phone_list in phone_numbers_by_customer.values() if len(phone_list) > 1)
    
    print(f"  - Total phone numbers collected: {total_phone_numbers}")
    print(f"  - Customers with multiple phone numbers: {customers_with_multiple_phones}")
    print(f"  - Average phone numbers per customer: {total_phone_numbers / len(phone_numbers_by_customer) if phone_numbers_by_customer else 0:.2f}")
    
    # Show sample data
    print(f"\n Sample phone numbers by customer ID:")
    sample_count = min(3, len(phone_numbers_by_customer))
    for i, (customer_id, phone_list) in enumerate(list(phone_numbers_by_customer.items())[:sample_count]):
        print(f"  - Customer {customer_id}: {phone_list}")
    
    print(f" SUCCESS! Extracted phone numbers for {len(phone_numbers_by_customer)} customers")
    return phone_numbers_by_customer


def get_all_emails_by_customer_id():
    """
    Get all emails matched to customer_id
    Returns a dictionary with customer_id as key and list of email objects as value
    Each email object contains 'email' and 'type' fields
    """
    print(" Extracting all emails by customer ID...")
    print("-" * 60)
    
    # Get the global customer data array
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return {}
    
    # Ensure we have the latest contact data
    print(" Ensuring contact data is up to date...")
    add_phone_numbers_to_customer_records()
    
    # Create dictionary with customer_id as key and email objects list as value
    emails_by_customer = {}
    
    for customer in global_customer_data_array:
        customer_id = customer.get('customer_id')
        emails_list = customer.get('emails', [])
        
        if customer_id and emails_list:
            emails_by_customer[customer_id] = emails_list
    
    print(f"\n Emails Summary:")
    print(f"  - Total customers with emails: {len(emails_by_customer)}")
    
    # Calculate statistics
    total_emails = sum(len(email_list) for email_list in emails_by_customer.values())
    customers_with_multiple_emails = sum(1 for email_list in emails_by_customer.values() if len(email_list) > 1)
    
    print(f"  - Total emails collected: {total_emails}")
    print(f"  - Customers with multiple emails: {customers_with_multiple_emails}")
    print(f"  - Average emails per customer: {total_emails / len(emails_by_customer) if emails_by_customer else 0:.2f}")
    
    # Show sample data
    print(f"\n Sample emails by customer ID:")
    sample_count = min(3, len(emails_by_customer))
    for i, (customer_id, email_list) in enumerate(list(emails_by_customer.items())[:sample_count]):
        print(f"  - Customer {customer_id}: {email_list}")
    
    print(f" SUCCESS! Extracted emails for {len(emails_by_customer)} customers")
    return emails_by_customer


def get_all_addresses_by_customer_id():
    """
    Get all addresses matched to customer_id
    Returns a dictionary with customer_id as key and list of address objects as value
    Each address object contains 'name', 'street', 'city', 'zip', 'address', 'createdOn', and 'modifiedOn' fields
    """
    print("Extracting all addresses by customer ID...")
    print("-" * 60)
    
    # Get the global customer data array
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return {}
    
    # Ensure we have the latest location data
    print(" Ensuring location data is up to date...")
    add_location_data_to_customer_records()
    
    # Create dictionary with customer_id as key and address objects list as value
    addresses_by_customer = {}
    
    for customer in global_customer_data_array:
        customer_id = customer.get('customer_id')
        addresses_list = customer.get('addresses', [])
        
        if customer_id and addresses_list:
            addresses_by_customer[customer_id] = addresses_list
    
    print(f"\n Addresses Summary:")
    print(f"  - Total customers with addresses: {len(addresses_by_customer)}")
    
    # Calculate statistics
    total_addresses = sum(len(address_list) for address_list in addresses_by_customer.values())
    customers_with_multiple_addresses = sum(1 for address_list in addresses_by_customer.values() if len(address_list) > 1)
    
    print(f"  - Total addresses collected: {total_addresses}")
    print(f"  - Customers with multiple addresses: {customers_with_multiple_addresses}")
    print(f"  - Average addresses per customer: {total_addresses / len(addresses_by_customer) if addresses_by_customer else 0:.2f}")
    
    # Show sample data
    print(f"\n Sample addresses by customer ID:")
    sample_count = min(3, len(addresses_by_customer))
    for i, (customer_id, address_list) in enumerate(list(addresses_by_customer.items())[:sample_count]):
        print(f"  - Customer {customer_id}: {len(address_list)} address(es)")
        for j, address in enumerate(address_list[:2]):  # Show first 2 addresses
            print(f"    Address {j+1}: {address.get('name', 'N/A')} - {address.get('street', 'N/A')}, {address.get('city', 'N/A')} {address.get('zip', 'N/A')}")
    
    print(f" SUCCESS! Extracted addresses for {len(addresses_by_customer)} customers")
    return addresses_by_customer


def get_all_contact_and_address_data_for_supabase():
    """
    Get all contact and address data formatted for Supabase insertion
    Returns a list of dictionaries with all phone numbers, emails, and address components
    """
    print(" Preparing all contact and address data for Supabase...")
    print("-" * 60)
    
    # Get the global customer data array
    global global_customer_data_array
    if not global_customer_data_array:
        print(" No customer data available in global array")
        return []
    
    # Ensure we have the latest data
    print(" Ensuring all data is up to date...")
    add_phone_numbers_to_customer_records()
    add_location_data_to_customer_records()
    
    # Prepare data for Supabase
    supabase_data = []
    
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
        
        # Create Supabase record
        supabase_record = {
            'customer_id': customer_id,
            'customer_name': customer.get('customer_name', ''),
            
            # All phone numbers
            'all_phone_numbers': all_phones,
            'phone_numbers_count': len(all_phones),
            'primary_phone': all_phones[0] if all_phones else '',
            
            # All emails
            'all_emails': all_emails,
            'emails_count': len(all_emails),
            'primary_email': all_emails[0] if all_emails else '',
            
            # All address components
            'all_streets': all_streets,
            'all_cities': all_cities,
            'all_zips': all_zips,
            'all_addresses': all_addresses,
            'addresses_count': len(all_addresses),
            
            # Primary address (from latest location)
            'primary_street': customer.get('location_street', ''),
            'primary_city': customer.get('location_city', ''),
            'primary_zip': customer.get('location_number', ''),
            'primary_address': customer.get('location_name', ''),
            
            # Additional customer data
            'is_vip': customer.get('is_vip', 'NO'),
            'business_unit_name': customer.get('business_unit_name', ''),
            'membership_type_id': customer.get('membership_type_id', ''),
            
            # Billing information
            'billingname': customer.get('billingname', []),
            'billingline1': customer.get('billingline1', [])
        }
        
        supabase_data.append(supabase_record)
    
    print(f"\n Supabase Data Summary:")
    print(f"  - Total customers processed: {len(supabase_data)}")
    
    # Calculate statistics
    customers_with_phones = sum(1 for record in supabase_data if record['all_phone_numbers'])
    customers_with_emails = sum(1 for record in supabase_data if record['all_emails'])
    customers_with_addresses = sum(1 for record in supabase_data if record['all_streets'])
    
    total_phones = sum(record['phone_numbers_count'] for record in supabase_data)
    total_emails = sum(record['emails_count'] for record in supabase_data)
    total_addresses = sum(record['addresses_count'] for record in supabase_data)
    
    print(f"  - Customers with phone numbers: {customers_with_phones}")
    print(f"  - Customers with emails: {customers_with_emails}")
    print(f"  - Customers with addresses: {customers_with_addresses}")
    print(f"  - Total phone numbers: {total_phones}")
    print(f"  - Total emails: {total_emails}")
    print(f"  - Total addresses: {total_addresses}")
    
    # Show sample data
    print(f"\n Sample Supabase data:")
    sample_count = min(3, len(supabase_data))
    for i in range(sample_count):
        record = supabase_data[i]
        print(f"  - Customer {record['customer_id']} ({record['customer_name']}):")
        print(f"    Phones ({record['phone_numbers_count']}): {record['all_phone_numbers']}")
        print(f"    Emails ({record['emails_count']}): {record['all_emails']}")
        print(f"    Streets ({len(record['all_streets'])}): {record['all_streets']}")
        print(f"    Cities ({len(record['all_cities'])}): {record['all_cities']}")
        print(f"    Zips ({len(record['all_zips'])}): {record['all_zips']}")
        print(f"    Address Names ({len(record['all_addresses'])}): {record['all_addresses']}")
    
    print(f" SUCCESS! Prepared {len(supabase_data)} customer records for Supabase")
    return supabase_data


def export_supabase_data_to_csv(filename="supabase_customer_data.csv"):
    """
    Export Supabase-formatted data to CSV
    """
    import csv
    
    print(f" Exporting Supabase data to {filename}...")
    
    # Get the Supabase data
    data = get_all_contact_and_address_data_for_supabase()
    
    if not data:
        print(" No data to export")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Define fieldnames for CSV
            fieldnames = [
                'customer_id', 'customer_name',
                'all_phone_numbers', 'phone_numbers_count', 'primary_phone',
                'all_emails', 'emails_count', 'primary_email',
                'all_streets', 'all_cities', 'all_zips', 'all_addresses', 'addresses_count',
                'primary_street', 'primary_city', 'primary_zip', 'primary_address',
                'is_vip', 'business_unit_name', 'membership_type_id',
                'billingname', 'billingline1'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for record in data:
                # Convert lists to strings for CSV
                record_copy = record.copy()
                
                # Convert list fields to semicolon-separated strings
                list_fields = ['all_phone_numbers', 'all_emails', 'all_streets', 'all_cities', 'all_zips', 'all_addresses', 'billingname', 'billingline1']
                
                for field in list_fields:
                    if field in record_copy and isinstance(record_copy[field], list):
                        record_copy[field] = '; '.join(str(item) for item in record_copy[field] if item)
                
                writer.writerow(record_copy)
        
        print(f" Successfully exported {len(data)} records to {filename}")
        return True
        
    except Exception as e:
        print(f" Error exporting to CSV: {e}")
        return False



