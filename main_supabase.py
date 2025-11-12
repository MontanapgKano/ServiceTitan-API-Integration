"""
Main script to demonstrate Supabase contacts data functionality
"""

from data_processor import (
    get_customers, 
    get_customer_contacts, 
    get_locations,
    add_phone_numbers_to_customer_records,
    add_location_data_to_customer_records
)
from supabase_data_formatter import get_supabase_contacts_data, export_supabase_contacts_to_csv

def main():
    """
    Main function to demonstrate the complete workflow
    """
    print("=" * 60)
    print("ServiceTitan to Supabase Data Processing")
    print("=" * 60)
    
    # Step 1: Get customers (with max_pages=1 for testing)
    print("\nStep 1: Fetching customers...")
    customers = get_customers()
    
    if not customers:
        print("No customers found. Please check your API credentials and connection.")
        return
    
    # Step 2: Get contacts
    print("\nStep 2: Fetching customer contacts...")
    contacts = get_customer_contacts()
    
    # Step 3: Get locations
    print("\nStep 3: Fetching locations...")
    locations = get_locations()
    
    # Step 4: Process and enrich data
    print("\nStep 4: Processing and enriching customer data...")
    add_phone_numbers_to_customer_records()
    add_location_data_to_customer_records()
    
    # Step 5: Get Supabase-formatted data
    print("\nStep 5: Preparing data for Supabase...")
    supabase_data = get_supabase_contacts_data()
    
    if supabase_data:
        # Step 6: Export to CSV
        print("\nStep 6: Exporting to CSV...")
        export_supabase_contacts_to_csv("supabase_contacts_data.csv")
        
        print("\n" + "=" * 60)
        print("SUCCESS! Data processing complete.")
        print("=" * 60)
        print(f"Processed {len(supabase_data)} customer records")
        print("Files created:")
        print("  - supabase_contacts_data.csv")
        print("\nNext steps:")
        print("1. Run the SQL script in supabase_table_setup.sql to create/update your Supabase table")
        print("2. Import the CSV data into your Supabase contacts table")
        print("3. Use the data in your Supabase application")
    else:
        print("No data was processed. Please check your API connection and data.")

if __name__ == "__main__":
    main()
