#!/bin/bash
# A simple script to add, commit, pull, and push changes to remote Git repositories.
# Usage: ./git_push.sh

set -e

git status

read -p "Enter commit message: " message

git add -A
git commit -m "$message"

# Push code
git push github main
git push gitlab main

# Ask about tagging
read -p "Create release tag? (y/n): " tagchoice
if [[ $tagchoice == "y" ]]; then
  read -p "Tag name (ex: v0.1.0): " tagname
  git tag -a $tagname -m "Release $tagname"
  git push github --tags
  git push gitlab --tags
fi

echo "Done ✔"