#!/bin/bash

# Script to initialize a GitHub repository for VideoProcessingPro and push code with sensitive files excluded

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}VideoProcessingPro GitHub Repository Setup${NC}"
echo "---------------------------------------"

# Ask for GitHub username
read -p "Enter your GitHub username: " github_username

# Ask for repository name
read -p "Enter repository name (default: VideoProcessingPro): " repo_name
repo_name=${repo_name:-VideoProcessingPro}

echo -e "\n${YELLOW}Creating GitHub repository: ${repo_name}${NC}"

# Check if git is already initialized
if [ -d .git ]; then
    echo -e "${YELLOW}Git repository already initialized.${NC}"
else
    echo "Initializing git repository..."
    git init
fi

# Check if .gitignore exists, create if not
if [ ! -f .gitignore ]; then
    echo "Creating .gitignore file..."
    cat > .gitignore << EOL
# Environment variables
.env
.env.*
!.env.example

# Streamlit secrets
.streamlit/secrets.toml

# Python virtual environments
venv/
.venv/
env/
__pycache__/
*.py[cod]
*$py.class

# Temporary files
*.tmp
temp/
tmp/

# Operating system files
.DS_Store
Thumbs.db

# IDE specific files
.idea/
.vscode/
*.swp
*.swo

# Media files
*.mp4
*.mov
*.avi
*.mp3
*.wav

# Large files
*.zip
*.tar.gz
*.7z

# Jupyter Notebook
.ipynb_checkpoints
EOL
fi

# Create repository on GitHub
echo -e "\n${YELLOW}Creating repository on GitHub...${NC}"
echo "Please enter your GitHub Personal Access Token (with 'repo' permissions):"
read -s github_token

# Use GitHub API to create repo
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    -H "Authorization: token $github_token" \
    -d "{\"name\":\"$repo_name\",\"description\":\"Video processing application using Gemini AI and Streamlit\",\"private\":false}" \
    https://api.github.com/user/repos)

if [ "$response" -eq 201 ] || [ "$response" -eq 200 ]; then
    echo -e "${GREEN}Repository created successfully!${NC}"
else
    echo -e "${RED}Failed to create repository. HTTP response code: $response${NC}"
    echo "You may need to create the repository manually on GitHub."
    read -p "Would you like to continue with pushing to an existing repository? (y/n): " continue_push
    if [ "$continue_push" != "y" ]; then
        exit 1
    fi
fi

# Add files to git
echo -e "\n${YELLOW}Adding files to git...${NC}"
git add .

# Commit files
echo -e "\n${YELLOW}Committing files...${NC}"
git commit -m "Initial commit of VideoProcessingPro"

# Add remote
echo -e "\n${YELLOW}Adding remote repository...${NC}"
git remote add origin https://github.com/$github_username/$repo_name.git

# Push to GitHub
echo -e "\n${YELLOW}Pushing to GitHub...${NC}"
git push -u origin master || git push -u origin main

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "Your code is now on GitHub at: ${BLUE}https://github.com/$github_username/$repo_name${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Deploy your app on Streamlit Cloud: https://streamlit.io/cloud"
echo "2. Add your API keys in the Streamlit Cloud app settings"
echo -e "3. Enjoy your deployed VideoProcessingPro app!\n" 