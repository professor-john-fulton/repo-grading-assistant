echo "Directory Tree:"

find . \
  ! -path "./.venv*" \
  ! -path "./.git*" \
  ! -path "./staticfiles*" \
  ! -path "*/__pycache__*" \
  ! -name "*.pyc" \
  | sed 's|[^/]*/|  |g'

echo "--------------------------------"
echo "Tracked Git Files:"
git ls-files

echo "--------------------------------"

echo "End of Report."
