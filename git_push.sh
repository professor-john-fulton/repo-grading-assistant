#!/bin/bash
# Add, commit, sync, test, and push changes to GitHub + GitLab.
# Usage: ./git_push.sh  (Git Bash)

set -euo pipefail

# Ensure remotes exist
git remote get-url github >/dev/null 2>&1 || { echo "Error: remote 'github' not configured"; exit 1; }
git remote get-url gitlab  >/dev/null 2>&1 || { echo "Error: remote 'gitlab' not configured"; exit 1; }


git status


# Extract version from pyproject.toml
version=$(grep -m 1 '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo ""
echo "📦 Current version: $version"
echo ""

read -r -p "Enter commit message: " message
if [[ -z "${message}" ]]; then
  echo "Error: commit message cannot be empty"
  exit 1
fi

git add -A
git commit -m "$message"

# Sync first (avoids push rejection)
git pull --rebase github main
git pull --rebase gitlab main

# ----------------------------
# TEST GATE (fails script on failure)
# ----------------------------
echo ""
echo "Running tests (ruff & pytest)..."
ruff check src tests --fix
python -m pytest
echo "Tests passed ✔"
echo ""

# Push code
git push github main
git push gitlab main

echo "Done ✔"
