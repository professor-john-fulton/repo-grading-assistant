#!/bin/bash
# Add, commit, sync, test, and push changes to GitHub + GitLab.
# Usage: ./git_push.sh  (Git Bash)

set -euo pipefail

# Ensure remotes exist
git remote get-url github >/dev/null 2>&1 || { echo "Error: remote 'github' not configured"; exit 1; }
git remote get-url gitlab  >/dev/null 2>&1 || { echo "Error: remote 'gitlab' not configured"; exit 1; }


git status

if git diff --quiet && git diff --cached --quiet; then
  echo ""
  read -r -p "No changes detected. Continue with tests and push anyway? (y/N): " continue_no_changes
  case "${continue_no_changes}" in
    [yY]|[yY][eE][sS])
      echo "Continuing without new commits."
      ;;
    *)
      echo "Aborted."
      exit 0
      ;;
  esac
fi


# Extract version from VERSION.py
version=$(python - <<'PY'
from VERSION import __version__
print(__version__)
PY
)
echo ""
echo "📦 Current version: $version"
echo ""

read -r -p "Enter commit message: " message
if [[ -z "${message}" ]]; then
  echo "Error: commit message cannot be empty"
  exit 1
fi

git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "$message"
fi

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
