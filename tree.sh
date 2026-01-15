find . \
  ! -path "./.venv*" \
  ! -path "./.git*" \
  ! -path "./staticfiles*" \
  ! -path "*/__pycache__*" \
  ! -name "*.pyc" \
  | sed 's|[^/]*/|  |g'