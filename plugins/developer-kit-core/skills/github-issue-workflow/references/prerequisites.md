# Prerequisites - Complete Reference

## Verification Commands

Before starting the GitHub Issue workflow, verify all required tools are available and properly configured.

### GitHub CLI

```bash
# Check if GitHub CLI is installed
gh --version

# Verify authentication (shows login status and scopes)
gh auth status

# If not authenticated, run:
gh auth login
# Follow prompts to authenticate with GitHub account
```

### Git Configuration

```bash
# Verify git is installed
git --version

# Check user name is configured
git config --get user.name
# If not set: git config --global user.name "Your Name"

# Check user email is configured
git config --get user.email
# If not set: git config --global user.email "your.email@example.com"

# Verify we're in a git repository
git rev-parse --git-dir

# Check git remote is configured
git remote -v
# Should show origin URL
```

### Repository Information

```bash
# Get repository owner and name
REPO_INFO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name')
echo "Repository: $REPO_INFO"

# Get default branch
TARGET_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | cut -d' ' -f5)
TARGET_BRANCH=${TARGET_BRANCH:-main}
echo "Default branch: $TARGET_BRANCH"

# Check if gh can access this repository
gh repo view
```

## Setup Instructions

### Install GitHub CLI

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install gh

# Fedora
sudo dnf install gh

# Arch Linux
sudo pacman -S gh
```

**Windows:**
```bash
winget install --id GitHub.cli
```

### Authenticate GitHub CLI

```bash
gh auth login
# Follow interactive prompts:
# 1. Choose account (GitHub.com or GitHub Enterprise)
# 2. Choose protocol (HTTPS or SSH)
# 3. Authenticate with browser or device code
```

### Configure Git

```bash
# Set your name (appears in commits)
git config --global user.name "Your Name"

# Set your email (must match GitHub account)
git config --global user.email "your.email@example.com"

# Optionally set default branch name
git config --global init.defaultBranch main
```

## Troubleshooting

### gh: command not found
- Install GitHub CLI using your package manager
- On macOS: `brew install gh`

### gh auth status shows "not logged in"
- Run `gh auth login` to authenticate
- Ensure your token has necessary scopes (repo, workflow)

### git: user.name not set
- Run `git config --global user.name "Your Name"`
- Run `git config --global user.email "your.email@example.com"`

### git remote not configured
- Ensure you're in a git repository: `git init` if needed
- Add remote: `git remote add origin <repository-url>`
