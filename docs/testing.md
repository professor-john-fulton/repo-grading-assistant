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
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --dry-run

python grade_assignments.py  \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --validate \
  --dry-run

python grade_assignments.py  \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --validate

python grade_assignments.py  \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --validate \
  --skip-scored

python grade_assignments.py \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --student student_2 \
  --dry-run

python grade_assignments.py  \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --student student_2 

python grade_assignments.py \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --student student_2 \
  --dry-run \
  --validate

python grade_assignments.py \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  


```