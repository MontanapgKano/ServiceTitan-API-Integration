# GitHub Actions Setup for Long-Running Data Pipeline

This document explains how to set up and use the GitHub Actions workflow for running your ServiceTitan to Supabase data pipeline that can execute for more than 8 hours.

## Overview

The workflow is designed to handle long-running data processing tasks that exceed GitHub's default 6-hour timeout limit for hosted runners. It includes:

- **10-hour timeout** (600 minutes) for the job
- **Comprehensive logging** with timestamps
- **Automatic artifact upload** for logs
- **Error handling** and notifications
- **Environment variable management**

## Required Secrets

You need to add the following secrets to your GitHub repository:

### ServiceTitan API Credentials
- `SERVICETITAN_CLIENT_ID` - Your ServiceTitan application client ID
- `SERVICETITAN_CLIENT_SECRET` - Your ServiceTitan application client secret  
- `SERVICETITAN_TENANT_ID` - Your ServiceTitan tenant ID

### Supabase Credentials
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase service role key (not anon key)

## How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the exact names listed above

## Workflow Triggers

The workflow will run automatically on:

- **Manual trigger** - Use "Actions" tab → "Long-Running Data Pipeline" → "Run workflow"
- **Daily schedule** - Every day at 2:00 AM UTC
- **Code changes** - When `main.py` or related Python files are pushed to main branch

## Workflow Features

### Timeout Management
- **Job timeout**: 10 hours (600 minutes)
- **Process timeout**: 9.5 hours (34200 seconds) - leaves buffer for cleanup
- **Logging**: All output is captured with timestamps

### Logging and Artifacts
- All pipeline output is logged to `logs/pipeline.log`
- Logs are uploaded as artifacts for both success and failure cases
- Success logs are kept for 7 days
- Failure logs are kept for 30 days

### Performance Optimizations
- **Dependency caching** - pip packages are cached between runs
- **Python optimizations** - `PYTHONUNBUFFERED=1` for real-time output
- **UTF-8 encoding** - `PYTHONIOENCODING=utf-8` for proper character handling

## Monitoring and Troubleshooting

### Viewing Logs
1. Go to **Actions** tab in your repository
2. Click on the latest workflow run
3. Click on the **run-pipeline** job
4. View real-time logs or download artifacts

### Common Issues

**Timeout Issues:**
- If the pipeline consistently times out, consider breaking it into smaller chunks
- Use the self-hosted runner option (commented in workflow) for unlimited runtime

**Authentication Errors:**
- Verify all secrets are correctly set
- Check that ServiceTitan credentials have proper permissions
- Ensure Supabase key has service role permissions

**Memory Issues:**
- The workflow uses `ubuntu-latest` which has 7GB RAM
- For larger datasets, consider using a self-hosted runner with more memory

## Self-Hosted Runner Option

For unlimited runtime (beyond 10 hours), you can use self-hosted runners:

1. Set up a self-hosted runner on your own infrastructure
2. Uncomment the `run-pipeline-self-hosted` job in the workflow
3. Comment out or remove the `run-pipeline` job
4. The self-hosted runner can run for up to 24 hours

## Customization

### Changing Schedule
Modify the cron expression in the workflow:
```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

### Adding Notifications
Add notification steps for Slack, email, or other services:
```yaml
- name: Notify Slack on completion
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Environment-Specific Configurations
You can create separate workflows for different environments (staging, production) by copying the workflow file and modifying the environment variables.

## Security Considerations

- All sensitive data is stored as GitHub secrets
- Logs may contain API responses - review before sharing
- Consider using environment-specific Supabase projects
- Regularly rotate API keys and secrets

## Cost Considerations

- GitHub-hosted runners are free for public repositories
- Private repositories have usage limits
- Self-hosted runners have no time limits but require your own infrastructure
- Consider the cost of API calls to ServiceTitan and Supabase

## Support

If you encounter issues:
1. Check the workflow logs in the Actions tab
2. Verify all secrets are correctly configured
3. Test the pipeline locally first
4. Review the ServiceTitan and Supabase API documentation


