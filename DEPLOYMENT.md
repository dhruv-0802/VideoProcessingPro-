# Deployment Guide for VideoProcessingPro

This guide explains how to deploy VideoProcessingPro to Streamlit Cloud while keeping your API keys secure.

## Prerequisites

- A GitHub account 
- A Streamlit account (sign up at [streamlit.io](https://streamlit.io) if you don't have one)
- Google Gemini API key

## Step 1: Upload your code to GitHub

### Option 1: Use the provided script (macOS/Linux)

Run the setup script in the project directory:

```bash
./setup_github_repo.sh
```

This script will:
1. Ask for your GitHub username
2. Create a new repository on GitHub
3. Push your code to the repository with sensitive files excluded

### Option 2: Manual GitHub upload

1. Create a new repository on GitHub
2. Initialize Git in your project folder (if not already initialized):
   ```bash
   git init
   ```
3. Add files to Git (make sure .env is in .gitignore):
   ```bash
   git add .
   ```
4. Commit the files:
   ```bash
   git commit -m "Initial commit of VideoProcessingPro"
   ```
5. Add the remote repository:
   ```bash
   git remote add origin https://github.com/yourusername/VideoProcessingPro.git
   ```
6. Push to GitHub:
   ```bash
   git push -u origin main
   ```

## Step 2: Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your Streamlit account
3. Click "New app"
4. Connect to your GitHub repository
5. Select the repository, branch, and main file (`streamlit_app.py`)

## Step 3: Configure Secrets in Streamlit Cloud

1. In your app settings on Streamlit Cloud, click on "Secrets"
2. Add your secrets in TOML format:

```toml
[api_keys]
google = "your_google_api_key_here"
```

3. Save the secrets

## Step 4: Deploy and Test

1. Deploy your app
2. Test the application by uploading a video file and processing it
3. Monitor the logs for any issues

## Troubleshooting

If you encounter any issues with API keys:

1. Verify that your secrets are correctly set in Streamlit Cloud
2. Check the application logs for error messages
3. Ensure your API keys are active and have the necessary permissions

## Security Best Practices

- Never commit API keys directly to your code
- Always use environment variables or Streamlit secrets
- Regularly rotate your API keys
- Consider implementing API key usage monitoring
- Use a private GitHub repository if your code contains sensitive information

## Local Development After Deployment

When developing locally after deployment:

1. Clone your repository
2. Create a local `.env` file with your API keys
3. Make and test your changes
4. Push your changes to GitHub
5. Streamlit Cloud will automatically redeploy your app

## Resources

- [Streamlit Deployment Documentation](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management) 