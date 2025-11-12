#!/usr/bin/env python3
"""
Main Orchestrator for ServiceTitan to Supabase Data Pipeline
Coordinates the three main components: ServiceTitan connection, data fetching, and Supabase storage
"""

import signal
import sys
import time
import platform
from servicetitan_connection import initialize_servicetitan_connection
from data_processor import (
    get_customers, get_global_customer_data, get_customer_ids,
    get_customer_contacts, get_contacts_data, get_locations, get_locations_data,
    get_invoices, get_invoices_data,
    get_memberships, get_memberships_data, get_jobs, get_jobs_data,
    get_business_units, get_business_units_data,
    add_phone_numbers_to_customer_records, add_location_data_to_customer_records,
    add_invoice_numbers_to_customer_records,
    add_membership_vip_status_to_customer_records, add_latest_business_unit_names_to_customer_records
)
from supabase_handler import initialize_supabase_connection, save_customers_to_supabase

# Global flag to track if timeout occurred
timeout_occurred = False

def timeout_handler(signum, frame):
    """Handle timeout signal (Unix/Linux only)"""
    global timeout_occurred
    timeout_occurred = True
    print("\n TIMEOUT: Process exceeded maximum runtime. Exiting gracefully...")
    print(" This may indicate an infinite loop or very large dataset.")
    print(" Consider reducing page_size or increasing max_pages limit.")
    sys.exit(1)

def setup_timeout():
    """Setup timeout handler based on platform"""
    if platform.system() != 'Windows':
        # Unix/Linux systems support SIGALRM
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(7200)  # 2 hours timeout
        return True
    else:
        # Windows doesn't support SIGALRM, we'll use a different approach
        print("WARNING: Windows detected: Timeout handler disabled (SIGALRM not supported)")
        return False


def main():
    """Main function to orchestrate the ServiceTitan to Supabase data pipeline"""
    
    print("DEBUG: Main function started")
    sys.stdout.flush()
    
    # Set up timeout handler (2 hours = 7200 seconds) - increased for very large datasets
    timeout_enabled = setup_timeout()
    
    print("ServiceTitan to Supabase Data Pipeline")
    print("=" * 60)
    print("Orchestrating data flow: ServiceTitan -> Raw Data -> Supabase")
    if timeout_enabled:
        print("Timeout set to 2 hours to prevent infinite loops")
    else:
        print("Timeout disabled on Windows - manual monitoring recommended")
    print("=" * 60)
    
    # Track start time and progress
    start_time = time.time()
    total_steps = 18  # Total number of steps in the pipeline
    current_step = 0
    
    def log_step(step_name):
        nonlocal current_step
        current_step += 1
        elapsed_time = time.time() - start_time
        print(f"\nProgress: Step {current_step}/{total_steps} - {step_name}")
        print(f"Elapsed time: {elapsed_time:.1f} seconds")
        print("-" * 50)
    
    # Step 1: Initialize ServiceTitan Connection
    log_step("Initializing ServiceTitan Connection")
    access_token, tenant_id, app_key = initialize_servicetitan_connection()
    
    if not access_token:
        print("ERROR: Failed to initialize ServiceTitan connection. Exiting.")
        return
    
    # Step 2: Initialize Supabase Connection
    log_step("Initializing Supabase Connection")
    if not initialize_supabase_connection():
        print("ERROR: Failed to initialize Supabase connection. Exiting.")
        return
    
    # Step 3: Retrieve Customer Data and Store in Global Array
    log_step("Retrieving Customer Data and Storing in Global Array")
    
    fetch_result = get_customers(
        tenant_id=tenant_id,
        app_key=app_key,
        page_size=100
    )
    
    if not fetch_result or not fetch_result.get('success'):
        print("ERROR: Customer data fetching failed. Exiting.")
        return
    
    # Get the data from global array
    customers_data = get_global_customer_data()
    if not customers_data:
        print("WARNING: No customer data in global array. Exiting.")
        return
    
    # Get customer IDs
    customer_ids_list = get_customer_ids()
    print(f"INFO: Customer IDs extracted: {len(customer_ids_list)}")
    if customer_ids_list:
        print(f"INFO: First 5 customer IDs: {customer_ids_list[:5]}")
    
    # Step 4: Fetch Customer Contacts
    log_step("Fetching Customer Contacts")
    
    contacts_result = get_customer_contacts(
        tenant_id=tenant_id,
        app_key=app_key,
        page_size=100
    )
    
    if not contacts_result or not contacts_result.get('success'):
        print("WARNING: Customer contacts fetching failed, but continuing with pipeline...")
    else:
        contacts_summary = contacts_result.get('summary', {})
        contacts_data = get_contacts_data()
        print(f"CONTACTS: Successfully fetched {len(contacts_data)} contacts")
        print(f"CONTACTS: Contacts processed: {contacts_summary.get('total_processed', 0)}")
        print(f"CONTACTS: Customers with contacts: {contacts_summary.get('customers_with_contacts', 0)}")
        print(f"CONTACTS: Pages processed: {contacts_summary.get('pages_processed', 0)}")
    
    # Step 5: Fetch Customer Locations
    log_step("Fetching Customer Locations")
    
    locations_result = get_locations(
        tenant_id=tenant_id,
        app_key=app_key,
        page_size=100
    )
    
    if not locations_result or not locations_result.get('success'):
        print("WARNING: Customer locations fetching failed, but continuing with pipeline...")
    else:
        locations_summary = locations_result.get('summary', {})
        locations_data = get_locations_data()
        print(f" Successfully fetched {len(locations_data)} locations")
        print(f" Locations processed: {locations_summary.get('total_processed', 0)}")
        print(f" Customers with locations: {locations_summary.get('customers_with_locations', 0)}")
        print(f" Pages processed: {locations_summary.get('pages_processed', 0)}")
    
    # Step 6: Fetch Invoices
    log_step("Fetching Invoices")
    
    invoices_result = get_invoices(
        tenant_id=tenant_id,
        app_key=app_key,
        page_size=100
    )
    
    if not invoices_result or not invoices_result.get('success'):
        print("WARNING: Invoices fetching failed, but continuing with pipeline...")
    else:
        invoices_summary = invoices_result.get('summary', {})
        invoices_data = get_invoices_data()
        print(f" Successfully fetched {len(invoices_data)} invoices")
        print(f" Invoices processed: {invoices_summary.get('total_processed', 0)}")
        print(f" Pages processed: {invoices_summary.get('pages_processed', 0)}")
    
    # Step 8: Fetch Memberships
    log_step("Fetching Memberships")
    
    memberships_result = get_memberships(
        tenant_id=tenant_id,
        app_key=app_key,
        page_size=100
    )
    
    if not memberships_result or not memberships_result.get('success'):
        print("WARNING: Memberships fetching failed, but continuing with pipeline...")
    else:
        memberships_summary = memberships_result.get('summary', {})
        memberships_data = get_memberships_data()
        print(f" Successfully fetched {len(memberships_data)} memberships")
        print(f" Memberships processed: {memberships_summary.get('total_processed', 0)}")
        print(f" Pages processed: {memberships_summary.get('pages_processed', 0)}")
    
    # Step 9: Fetch Jobs
    log_step("Fetching Jobs")
    
    jobs_result = get_jobs(
        tenant_id=tenant_id,
        app_key=app_key,
        page_size=100
    )
    
    if not jobs_result or not jobs_result.get('success'):
        print("WARNING: Jobs fetching failed, but continuing with pipeline...")
    else:
        jobs_summary = jobs_result.get('summary', {})
        jobs_data = get_jobs_data()
        print(f" Successfully fetched {len(jobs_data)} jobs")
        print(f" Jobs processed: {jobs_summary.get('total_processed', 0)}")
        print(f" Pages processed: {jobs_summary.get('pages_processed', 0)}")
    
    # Step 10: Fetch Job Types
    log_step("Fetching Job Types")
    
    business_units_result = get_business_units(
        tenant_id=tenant_id,
        app_key=app_key,
        page_size=100
    )
    
    if not business_units_result or not business_units_result.get('success'):
        print("WARNING: Business units fetching failed, but continuing with pipeline...")
    else:
        business_units_summary = business_units_result.get('summary', {})
        business_units_data = get_business_units_data()
        print(f" Successfully fetched {len(business_units_data)} business units")
        print(f"Business units processed: {business_units_summary.get('total_processed', 0)}")
    # Step 11: Add Phone Numbers to Customer Records
    log_step("Adding Phone Numbers to Customer Records")
    
    add_phone_numbers_to_customer_records()
    
    # Step 12: Add Location Data to Customer Records
    log_step("Adding Location Data to Customer Records")
    
    add_location_data_to_customer_records()
    
    # Step 13: Add Invoice Numbers to Customer Records
    log_step("Adding Invoice Numbers to Customer Records")
    
    add_invoice_numbers_to_customer_records()
    
    # Step 14: Add VIP Status to Customer Records
    log_step("Adding VIP Status to Customer Records")
    
    add_membership_vip_status_to_customer_records()
    
    # Step 15: Add Latest Job Type Names to Customer Records
    log_step("Adding Latest Job Type Names to Customer Records")
    
    add_latest_business_unit_names_to_customer_records()
    
    # Step 16: Save Customer Data to Supabase
    log_step("Saving Customer Data to Supabase")
    
    save_result = save_customers_to_supabase(customers_data)
    
    # Step 17: Display Final Results
    log_step("Displaying Final Results Summary")
    
    # Fetch summary
    fetch_summary = fetch_result.get('summary', {})
    print(f" Data Fetching:")
    print(f"  - Total customers fetched: {fetch_summary.get('total_processed', 0)}")
    print(f"  - Pages processed: {fetch_summary.get('pages_processed', 0)}")
    print(f"  - Customers stored in global array: {len(customers_data)}")
    print(f"  - Customer IDs extracted: {len(customer_ids_list)}")
    
    # Contacts summary
    contacts_summary = contacts_result.get('summary', {}) if contacts_result else {}
    print(f" Contacts Information:")
    print(f"  - Contacts fetch success: {'SUCCESS: Yes' if contacts_result and contacts_result.get('success') else 'ERROR: No'}")
    print(f"  - Total contacts fetched: {len(contacts_data) if 'contacts_data' in locals() else 0}")
    print(f"  - Contacts processed: {contacts_summary.get('total_processed', 0)}")
    print(f"  - Customers with contacts: {contacts_summary.get('customers_with_contacts', 0)}")
    print(f"  - Batches processed: {contacts_summary.get('batches_processed', 0)}")
    
    # Locations summary
    locations_summary = locations_result.get('summary', {}) if locations_result else {}
    print(f" Locations Information:")
    print(f"  - Locations fetch success: {'SUCCESS: Yes' if locations_result and locations_result.get('success') else 'ERROR: No'}")
    print(f"  - Total locations fetched: {len(locations_data) if 'locations_data' in locals() else 0}")
    print(f"  - Locations processed: {locations_summary.get('total_processed', 0)}")
    print(f"  - Customers with locations: {locations_summary.get('customers_with_locations', 0)}")
    print(f"  - Pages processed: {locations_summary.get('pages_processed', 0)}")
    
    # Invoices summary
    invoices_summary = invoices_result.get('summary', {}) if invoices_result else {}
    print(f" Invoices Information:")
    print(f"  - Invoices fetch success: {'SUCCESS: Yes' if invoices_result and invoices_result.get('success') else 'ERROR: No'}")
    print(f"  - Total invoices fetched: {len(invoices_data) if 'invoices_data' in locals() else 0}")
    print(f"  - Invoices processed: {invoices_summary.get('total_processed', 0)}")
    print(f"  - Pages processed: {invoices_summary.get('pages_processed', 0)}")
    
    # Memberships summary
    memberships_summary = memberships_result.get('summary', {}) if memberships_result else {}
    print(f" Memberships Information:")
    print(f"  - Memberships fetch success: {'SUCCESS: Yes' if memberships_result and memberships_result.get('success') else 'ERROR: No'}")
    print(f"  - Total memberships fetched: {len(memberships_data) if 'memberships_data' in locals() else 0}")
    print(f"  - Memberships processed: {memberships_summary.get('total_processed', 0)}")
    print(f"  - Pages processed: {memberships_summary.get('pages_processed', 0)}")
    
   
    # Supabase save summary
    print(f" Supabase Storage:")
    print(f"  - Total customers saved: {save_result.get('total_processed', 0)}")
    print(f"  - New customers inserted: {save_result.get('total_inserted', 0)}")
    print(f"  - Existing customers updated: {save_result.get('total_updated', 0)}")
    print(f"  - Errors encountered: {save_result.get('total_errors', 0)}")
    
    # Overall success
    overall_success = fetch_result.get('success', False) and save_result.get('success', False)
    
    if overall_success:
        print("\nSUCCESS! Customer data pipeline executed successfully!")
    else:
        print("\nWARNING: Pipeline completed with some issues. Check the logs above for details.")
    
    print("=" * 60)
    
    # Cancel the timeout alarm since we completed successfully (if timeout was enabled)
    if timeout_enabled:
        signal.alarm(0)
    total_elapsed_time = time.time() - start_time
    print(f"Pipeline completed successfully within timeout limit!")
    print(f"Total execution time: {total_elapsed_time:.1f} seconds ({total_elapsed_time/60:.1f} minutes)")


if __name__ == "__main__":
    try:
        print("DEBUG: Script started")
        sys.stdout.flush()
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
