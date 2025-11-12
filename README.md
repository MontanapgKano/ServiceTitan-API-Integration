# ServiceTitan to Supabase Data Pipeline

This simplified pipeline fetches customer data from the ServiceTitan API and stores it in a Supabase database. The system focuses on core customer data retrieval and storage functionality.

## Architecture

The pipeline consists of three main modules:

1. **ServiceTitan Connection** (`servicetitan_connection.py`) - Handles API authentication, token management, and API requests
2. **Data Processor** (`data_processor.py`) - Processes and transforms ServiceTitan data
3. **Supabase Handler** (`supabase_handler.py`) - Manages database operations and data storage

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file with your API credentials:

```bash
# ServiceTitan API Configuration
SERVICETITAN_TENANT_ID=your_actual_tenant_id
SERVICETITAN_CLIENT_ID=your_actual_client_id
SERVICETITAN_CLIENT_SECRET=your_actual_client_secret
SERVICETITAN_APP_KEY=your_actual_app_key

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_TABLE_NAME=clients
```

### 3. Get ServiceTitan API Credentials

1. Go to [ServiceTitan Developer Portal](https://developer.servicetitan.io/)
2. Sign in with your ServiceTitan account
3. Create a new application
4. Get your:
   - **Tenant ID**: Found in your ServiceTitan account settings
   - **Client ID**: OAuth 2.0 Client ID from your app registration
   - **Client Secret**: OAuth 2.0 Client Secret from your app registration
   - **App Key**: ServiceTitan App Key from your app registration

### 4. Get Supabase Credentials

1. Go to [Supabase](https://supabase.com/)
2. Create a new project
3. Get your:
   - **Project URL**: Found in your project settings
   - **API Key**: Found in your project API settings
   - **Table Name**: The name of your customers table (default: 'clients')

### 5. Run the Pipeline

```bash
python main.py
```

## Output

The pipeline will:
- Fetch all customer data from ServiceTitan API
- Process customer details including names, addresses, and tag types
- Save the data to your Supabase database
- Provide detailed progress logs and summary statistics

## Module Details

### ServiceTitan Connection Module
- Handles OAuth 2.0 authentication
- Manages token refresh automatically
- Provides retry logic for API requests
- Validates configuration

### Data Processor Module
- Fetches and processes customer data
- Extracts customer IDs for further processing
- Manages customer data storage in global arrays

### Supabase Handler Module
- Manages database connections
- Handles insert/update operations
- Provides connection testing
- Manages data preparation for database

## Configuration Options

You can customize the following in your `.env` file:

- `SERVICETITAN_TENANT_ID`: Your ServiceTitan tenant ID
- `SERVICETITAN_CLIENT_ID`: Your ServiceTitan client ID
- `SERVICETITAN_CLIENT_SECRET`: Your ServiceTitan client secret
- `SERVICETITAN_APP_KEY`: Your ServiceTitan app key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key
- `SUPABASE_TABLE_NAME`: Your Supabase table name (default: 'clients')

## Security Notes

- The `.env` file contains sensitive credentials and is excluded from version control
- Never commit your actual API credentials to the repository
- Keep your credentials secure and rotate them regularly
- Use environment variables for production deployments

## Troubleshooting

### ServiceTitan Authentication Issues
1. Verify your credentials in the `.env` file
2. Check that your ServiceTitan app has the correct permissions
3. Ensure your app is properly configured in the ServiceTitan developer portal

### Supabase Connection Issues
1. Verify your SUPABASE_URL and SUPABASE_KEY are correct
2. Check your internet connection
3. Ensure the Supabase table exists and has the correct schema

### General Issues
1. Check the console output for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure you have the required permissions for both ServiceTitan and Supabase

## Files Structure

```
From ServiceTitan To Supabase/
├── .env                           # Environment variables (not in git)
├── .gitignore                     # Git ignore rules
├── main.py                        # Main orchestrator script (simplified)
├── servicetitan_connection.py     # ServiceTitan API connection module
├── data_processor.py              # Data processing module (customer data only)
├── supabase_handler.py            # Supabase database handler
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── supabase_table_setup.sql       # SQL for Supabase table setup
```

## Migration from Legacy Script

If you're migrating from the old `data_pulling.py` script:

1. The new simplified structure focuses on core customer data functionality
2. All configuration remains the same
3. The main entry point is now `main.py` instead of `data_pulling.py`
4. The pipeline now only fetches and stores customer data (no additional data processing)
5. The old script is preserved for reference but is deprecated

## Performance Features

- **Streaming Processing**: Customers are processed as they are fetched to reduce memory usage
- **Token Management**: Automatic token refresh prevents authentication failures
- **Retry Logic**: Built-in retry mechanisms for failed API requests
- **Batch Operations**: Efficient database operations with proper error handling
- **Progress Tracking**: Detailed logging and progress indicators
- **Simplified Architecture**: Focused on core customer data functionality for better performance

