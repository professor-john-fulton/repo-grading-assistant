# Testing


## How to run automated tests

    - pytest
    - pytest -v
    - pytest -v | tee tests/test_run.log
    - pytest -v --cov=src.repo-grading-assistant.grade_assignments | tee tests/test_run.log
    - pytest -v --cov=src.repo-grading-assistant.grade_assignments --cov-report=term-missing 2>&1 | tee tests/test_run.log
    - pytest -v --cov=src.repo-grading-assistant.grade_assignments --cov-report=term-missing 2>&1 | tee tests/test_run.log


## Manual Tests

```bash

repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --dry-run

repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --validate \
  --dry-run

repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --validate

repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --validate \
  --skip-scored

repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --student student_2 \
  --dry-run

repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --student student_2 

repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --student student_2 \
  --dry-run \
  --validate

repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  


```