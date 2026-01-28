# Testing


## How to run automated tests

```bash
pytest
pytest -v
pytest -v | tee tests/test_run.log
pytest -v --cov=src/repo_grading_assistant/grade_assignments --cov-report=term-missing
pytest -v --cov=src/repo_grading_assistant/grade_assignments --cov-report=term-missing 2>&1 | tee tests/test_run.log
pytest -v --cov=src/repo_grading_assistant --cov-report=html --cov-report=term-missing
```

### OpenAI API Validation

The test suite includes one test that calls the actual OpenAI API to validate configuration:
- `test_openai_api_access_and_response` - Validates API key and model access
- Runs automatically with every `pytest` execution
- Incurs minimal cost (~$0.001 per test run)
- Skips automatically if `OPENAI_API_KEY` is not set

**Requirements:**
- `OPENAI_API_KEY` must be set in `.env` file
- API key must have access to `gpt-5-mini` model


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