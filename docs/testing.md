# Testing


## How to run automated tests

    - pytest
    - pytest -v
    - pytest -v | tee tests/test_run.log
    - pytest -v --cov=grade_assignments | tee tests/test_run.log
    - pytest -v --cov=grade_assignments --cov-report=term-missing 2>&1 | tee tests/test_run.log
    - pytest -v --cov=grade_assignments --cov-report=term-missing 2>&1 | tee tests/test_run.log


## Manual Tests

```bash
python grade_assignments.py  \
  --config configs/lab05_config.json  \
  --repo-root /D/Exercises/25FA/ITEC660/Lab05  \
  --dry-run

python grade_assignments.py  \
  --config configs/lab05_config.json  \
  --repo-root /D/Exercises/25FA/ITEC660/Lab05  \
  --validate

python grade_assignments.py  \
  --config configs/lab05_config.json  \
  --repo-root /D/Exercises/25FA/ITEC660/Lab05  \
  --validate \
  --dry-run

python grade_assignments.py \
  --config configs/lab05_config.json  \
  --repo-root /D/Exercises/25FA/ITEC660/Lab05 \
  --student lab-5-wmbucha \
  --dry-run

python grade_assignments.py  \
  --config configs/lab05_config.json  \
  --repo-root /D/Exercises/25FA/ITEC660/Lab05  \
  --validate \
  --skip-scored

python grade_assignments.py  \
  --config configs/lab05_config.json  \
  --repo-root /D/Exercises/25FA/ITEC660/Lab05  \
  --dry-run --validate   --student lab-5-professor-john-fulton

python grade_assignments.py  \
  --config configs/lab05_config.json  \
  --repo-root /D/Exercises/25FA/ITEC660/Lab05  \
  --student lab-5-professor-john-fulton
```