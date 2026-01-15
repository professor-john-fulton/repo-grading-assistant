#!/bin/bash
# Add, commit, sync, and push changes to GitHub + GitLab.
# Usage: ./git_push.sh

set -euo pipefail

# Ensure remotes exist
git remote get-url github >/dev/null 2>&1 || { echo "Error: remote 'github' not configured"; exit 1; }
git remote get-url gitlab >/dev/null 2>&1 || { echo "Error: remote 'gitlab' not configured"; exit 1; }

git status

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

# Push code
git push github main
git push gitlab main

echo "Done ✔"
