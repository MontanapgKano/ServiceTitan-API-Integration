-- Supabase table setup for ServiceTitan customer-contact data
-- Run this SQL in your Supabase SQL editor to create/update the table

-- Drop existing table if it exists (uncomment if you want to recreate)
-- DROP TABLE IF EXISTS contacts;

CREATE TABLE IF NOT EXISTS test_contacts (
    id BIGSERIAL PRIMARY KEY,
    customer_id TEXT,                  -- ServiceTitan customer ID for indexing
    contactname TEXT,                  -- Customer name from customer data
    
    -- All phone numbers
    all_phone_numbers TEXT,            -- All phone numbers (semicolon-separated)
    
    -- All emails
    all_emails TEXT,                   -- All email addresses (semicolon-separated)
    
    -- All address components
    all_streets TEXT,                  -- All street addresses (JSON array or semicolon-separated)
    all_cities TEXT,                   -- All cities (JSON array or semicolon-separated)
    all_zips TEXT,                     -- All zip codes (JSON array or semicolon-separated)
    all_addresses TEXT,            -- All address/location names (JSON array or semicolon-separated)
    
    -- Primary address (latest)
    primary_street TEXT,               -- Primary street from latest location
    primary_city TEXT,                 -- Primary city from latest location
    primary_zip TEXT,                  -- Primary zip from latest location
    primary_address TEXT,         -- Primary address name from latest location
    
    -- Additional fields
    is_vip TEXT,                       -- VIP status based on membership type ID (YES/NO)
    business_unit_name TEXT,           -- Business unit name from latest job
    billingname TEXT,                  -- Invoice reference numbers (JSON array)
    billingline1 TEXT,                 -- Invoice dates (JSON array)
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_contacts_customer_id ON contacts(customer_id);
CREATE INDEX IF NOT EXISTS idx_contacts_contactname ON contacts(contactname);
CREATE INDEX IF NOT EXISTS idx_contacts_primary_city ON contacts(primary_city);
CREATE INDEX IF NOT EXISTS idx_contacts_primary_zip ON contacts(primary_zip);
CREATE INDEX IF NOT EXISTS idx_contacts_billingname ON contacts(billingname);
CREATE INDEX IF NOT EXISTS idx_contacts_billingline1 ON contacts(billingline1);
CREATE INDEX IF NOT EXISTS idx_contacts_is_vip ON contacts(is_vip);
CREATE INDEX IF NOT EXISTS idx_contacts_business_unit_name ON contacts(business_unit_name);
CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts(created_at);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on row updates
DROP TRIGGER IF EXISTS update_contacts_updated_at ON contacts;
CREATE TRIGGER update_contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Migration script for existing tables (run this if you have an old table structure)
-- Uncomment and run these statements if you need to migrate from the old structure

-- Drop old columns that are no longer needed (uncomment if needed)
-- ALTER TABLE contacts DROP COLUMN IF EXISTS name;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS address;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS phone;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS last_job;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS invoice_numbers;  -- Replaced by billingname and billingline1
-- ALTER TABLE contacts DROP COLUMN IF EXISTS membership;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS is_vip;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS location_city;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS location_address;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS location_number;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS location_tag_type_names;
-- ALTER TABLE contacts DROP COLUMN IF EXISTS location_name;

-- Migration from invoice_numbers to billingname/billingline1 (run this if you have existing data)
-- This will help migrate existing invoice_numbers data to the new format
-- Note: This is a basic migration - you may need to adjust based on your data format
-- UPDATE contacts SET 
--     billingname = CASE 
--         WHEN invoice_numbers IS NOT NULL AND invoice_numbers != '' 
--         THEN '["' || REPLACE(invoice_numbers, ',', '","') || '"]'
--         ELSE 'No Billing Names'
--     END,
--     billingline1 = 'No Billing Dates'
-- WHERE billingname IS NULL OR billingname = 'No Billing Names';

-- Add new columns to existing table (run these if table already exists)
-- These statements are safe to run multiple times
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS customer_id TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS contactname TEXT;

-- All phone numbers
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS all_phone_numbers TEXT;

-- All emails
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS all_emails TEXT;

-- All address components
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS all_streets TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS all_cities TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS all_zips TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS all_addresses TEXT;

-- Primary address (latest)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS primary_street TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS primary_city TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS primary_zip TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS primary_address TEXT;

-- Additional fields
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS is_vip TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS business_unit_name TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS billingname TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS billingline1 TEXT;

-- Add comments to the table and columns
COMMENT ON TABLE contacts IS 'ServiceTitan customer and location data with all addresses, phones, and emails';
COMMENT ON COLUMN contacts.customer_id IS 'ServiceTitan customer ID for indexing';
COMMENT ON COLUMN contacts.contactname IS 'Customer name from customer data';

-- Phone number comments
COMMENT ON COLUMN contacts.all_phone_numbers IS 'All phone numbers (semicolon-separated)';

-- Email comments
COMMENT ON COLUMN contacts.all_emails IS 'All email addresses (semicolon-separated)';

-- Address comments
COMMENT ON COLUMN contacts.all_streets IS 'All street addresses (semicolon-separated)';
COMMENT ON COLUMN contacts.all_cities IS 'All cities (semicolon-separated)';
COMMENT ON COLUMN contacts.all_zips IS 'All zip codes (semicolon-separated)';
COMMENT ON COLUMN contacts.all_addresses IS 'All address/location names (semicolon-separated)';

-- Primary address comments
COMMENT ON COLUMN contacts.primary_street IS 'Primary street from latest location';
COMMENT ON COLUMN contacts.primary_city IS 'Primary city from latest location';
COMMENT ON COLUMN contacts.primary_zip IS 'Primary zip from latest location';
COMMENT ON COLUMN contacts.primary_address IS 'Primary address name from latest location';

-- Additional field comments
COMMENT ON COLUMN contacts.is_vip IS 'VIP status based on membership type ID (YES/NO)';
COMMENT ON COLUMN contacts.business_unit_name IS 'Business unit name from latest job';
COMMENT ON COLUMN contacts.billingname IS 'Invoice reference numbers (JSON array)';
COMMENT ON COLUMN contacts.billingline1 IS 'Invoice dates (JSON array)';
COMMENT ON COLUMN contacts.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN contacts.updated_at IS 'Record last update timestamp';

-- Example queries for testing
-- SELECT * FROM contacts WHERE customer_id = 'your_customer_id';
-- SELECT COUNT(*) FROM contacts;
-- SELECT * FROM contacts ORDER BY updated_at DESC LIMIT 10;