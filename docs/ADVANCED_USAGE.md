# Advanced Usage Guide

This guide covers advanced workflows and scenarios for experienced users of the Repo Grading Assistant.

---

## Table of Contents

- [Re-grading Workflows](#re-grading-workflows)
- [Handling Partial Submissions](#handling-partial-submissions)
- [Batch Processing Strategies](#batch-processing-strategies)
- [Late Submission Handling](#late-submission-handling)
- [Custom Grading Workflows](#custom-grading-workflows)
- [Managing Multiple Assignments](#managing-multiple-assignments)
- [Integration with LMS](#integration-with-lms)
- [Advanced Configuration](#advanced-configuration)

---

## Re-grading Workflows

### Scenario 1: Updated Grading Rubric

**Problem:** You refined your grading criteria after grading some students.

**Solution - Re-grade All Students:**

```bash
# Back up existing results first
cp -r logs logs_backup_$(date +%Y%m%d)
cp -r */grade_summary.txt .  # If you want to keep old reports

# Update your grading key file
nano keys/assignment_key.txt  # Make your changes

# Re-grade everyone
repo-grading-assistant --config my_config.json

# The tool will:
# - Overwrite existing grade_summary.txt files
# - Append new rows to CSV (you may want to clean this up)
```

**Solution - Clean CSV Before Re-grading:**

```bash
# Remove all but header row from CSV
head -n 1 logs/grading_summary.csv > logs/grading_summary_new.csv
mv logs/grading_summary_new.csv logs/grading_summary.csv

# Now re-grade
repo-grading-assistant --config my_config.json
```

---

### Scenario 2: Re-grade Single Student

**Problem:** One student disputed their grade or resubmitted.

**Solution:**

```bash
# Re-grade just that student
repo-grading-assistant \
  --config my_config.json \
  --student student_alice

# This overwrites their grade_summary.txt
# You'll need to manually update the CSV
```

**Manually Update CSV:**

```bash
# Option 1: Edit CSV directly
nano logs/grading_summary.csv  # Find and update the student's row

# Option 2: Remove student's old row and re-run
grep -v "student_alice" logs/grading_summary.csv > logs/temp.csv
mv logs/temp.csv logs/grading_summary.csv
repo-grading-assistant --config my_config.json --student student_alice
```

---

### Scenario 3: Comparing Old vs New Grades

**Problem:** Want to see how grades changed after rubric adjustment.

**Solution:**

```bash
# Before re-grading, save current results
mkdir comparison
cp logs/grading_summary.csv comparison/old_grades.csv

# Re-grade with new rubric
repo-grading-assistant --config my_config.json

# Compare
cp logs/grading_summary.csv comparison/new_grades.csv

# Use diff or spreadsheet to compare
diff comparison/old_grades.csv comparison/new_grades.csv

# Or with Python/pandas:
python -c "
import pandas as pd
old = pd.read_csv('comparison/old_grades.csv')
new = pd.read_csv('comparison/new_grades.csv')
comparison = pd.merge(old, new, on='student_folder', suffixes=('_old', '_new'))
comparison['grade_change'] = comparison['grade_new'] - comparison['grade_old']
comparison[['student_folder', 'grade_old', 'grade_new', 'grade_change']].to_csv('comparison/comparison.csv', index=False)
print('Comparison saved to comparison/comparison.csv')
"
```

---

## Handling Partial Submissions

### Scenario 1: Student Missing Required Files

**Problem:** Student's submission is incomplete.

**Current Behavior:**
- Tool reports missing files in grade_summary.txt
- Grading proceeds based on what's available
- Grade reflects incomplete submission

**Manual Intervention:**

```bash
# After grading, review students with missing files
grep -l "MISSING FILES" */grade_summary.txt

# For each incomplete submission:
# 1. Contact student for complete submission
# 2. When received, copy files into their folder
# 3. Re-grade that student:

repo-grading-assistant --config my_config.json --student student_incomplete
```

---

### Scenario 2: Student Submitted to Wrong Location

**Problem:** Student put files in unexpected structure.

**Solution - Adjust File Patterns:**

**Option 1 - Use flexible patterns:**

```json
{
  "required_files": [
    "**/main.py",      // Finds main.py anywhere
    "**/*.css",        // Finds all CSS files
    "**/models.py"     // Finds models.py at any level
  ]
}
```

**Option 2 - Reorganize student folder:**

```bash
# Create proper structure
mkdir -p student_bob/src
mv student_bob/*.py student_bob/src/

# Re-grade
repo-grading-assistant --config my_config.json --student student_bob
```

---

### Scenario 3: Partial Credit for Incomplete Work

**Problem:** Want to award partial credit systematically.

**Solution - Update grading key with partial credit guidelines:**

```text
# In your grading key:

- Authentication system (15 points total):
  * User registration (5 points)
  * Login/logout (5 points)
  * Password reset (5 points)
*** +15 points (award partial credit proportionally)

Instructions to AI:
- Award 10/15 if only registration and login implemented
- Award 5/15 if only basic login works
- Award 0/15 if authentication missing entirely
```

The AI will follow these guidelines when evaluating.

---

## Batch Processing Strategies

### Scenario 1: Large Class (100+ Students)

**Problem:** Grading 100+ students takes time and risks API rate limits.

**Solution - Process in Batches:**

```bash
# Split students into batches
mkdir batch1 batch2 batch3

# Move students (or use symlinks)
mv student_{1..33} batch1/
mv student_{34..66} batch2/
mv student_{67..100} batch3/

# Process each batch
for batch in batch1 batch2 batch3; do
  echo "Processing $batch..."
  repo-grading-assistant \
    --config my_config.json \
    --repo-root $batch
  
  # Wait between batches to avoid rate limits
  echo "Waiting 60 seconds before next batch..."
  sleep 60
done

# Consolidate results
cat batch*/logs/grading_summary.csv > logs/all_grades.csv
```

---

### Scenario 2: Parallel Processing Different Assignments

**Problem:** Multiple assignments to grade simultaneously.

**Solution:**

```bash
# Create separate directories for each assignment
assignments/
├── lab3/
│   ├── config.json
│   ├── key.txt
│   └── students/
├── lab4/
│   ├── config.json
│   ├── key.txt
│   └── students/
└── lab5/
    ├── config.json
    ├── key.txt
    └── students/

# Grade each assignment (can run in separate terminals)
cd assignments/lab3
repo-grading-assistant --config config.json --repo-root students

cd assignments/lab4
repo-grading-assistant --config config.json --repo-root students

cd assignments/lab5
repo-grading-assistant --config config.json --repo-root students

# Each creates its own logs/ directory
```

---

### Scenario 3: Resume After Interruption

**Problem:** Process interrupted (network issue, ctrl-c, etc.).

**Solution - Skip Already Graded:**

```bash
# Use --skip-scored flag to skip students with existing grade_summary.txt
repo-grading-assistant \
  --config my_config.json \
  --skip-scored

# This resumes where you left off
```

**Manual Resume:**

```bash
# Find which students are complete
for dir in student_*/; do
  if [ -f "$dir/grade_summary.txt" ]; then
    echo "✓ $dir"
  else
    echo "✗ $dir (needs grading)"
  fi
done

# Grade remaining students individually
for dir in student_*/; do
  if [ ! -f "$dir/grade_summary.txt" ]; then
    echo "Grading $dir..."
    repo-grading-assistant \
      --config my_config.json \
      --student "$(basename $dir)"
  fi
done
```

---

## Late Submission Handling

### Scenario 1: Automatic Late Penalty

**Problem:** Need to apply late penalties based on submission date.

**Solution - Post-processing Script:**

```python
# late_penalty.py
import pandas as pd
from datetime import datetime

# Load grades
df = pd.read_csv('logs/grading_summary.csv')

# Late policy: 10% per day, max 3 days
due_date = datetime(2026, 2, 1)

def apply_late_penalty(row):
    # Parse submission date from timestamp
    submit_date = datetime.fromisoformat(row['timestamp'])
    days_late = max(0, (submit_date - due_date).days)
    
    if days_late == 0:
        return row['grade']
    elif days_late <= 3:
        penalty = 0.10 * days_late
        return row['grade'] * (1 - penalty)
    else:
        return 0  # More than 3 days late: no credit

df['grade_adjusted'] = df.apply(apply_late_penalty, axis=1)
df['days_late'] = df.apply(
    lambda row: max(0, (datetime.fromisoformat(row['timestamp']) - due_date).days),
    axis=1
)

df.to_csv('logs/grading_summary_with_penalties.csv', index=False)
print("Late penalties applied. See grading_summary_with_penalties.csv")
```

**Run after grading:**

```bash
repo-grading-assistant --config my_config.json
python late_penalty.py
```

---

### Scenario 2: Separate Late Submissions

**Problem:** Some students submit late; want to process separately.

**Solution:**

```bash
# Create separate folders
mkdir on_time late_submissions

# Move students to appropriate folder
mv student_{alice,bob,charlie} on_time/
mv student_{david,eve} late_submissions/

# Grade on-time submissions first
repo-grading-assistant \
  --config my_config.json \
  --repo-root on_time

# Later, grade late submissions with different key or notes
repo-grading-assistant \
  --config my_config_late.json \
  --repo-root late_submissions
```

---

### Scenario 3: Resubmissions After Feedback

**Problem:** Allow students to improve and resubmit.

**Solution:**

```bash
# Original submission grading
repo-grading-assistant --config my_config.json

# Save original grades
cp logs/grading_summary.csv logs/original_grades.csv

# After resubmissions received:
# Copy new files into student folders (overwriting old)

# Create resubmission grading key (maybe more lenient or different focus)
cp keys/original_key.txt keys/resubmission_key.txt
nano keys/resubmission_key.txt  # Adjust criteria

# Update config to use resubmission key
# Re-grade
repo-grading-assistant --config my_config_resubmission.json

# Take higher of two grades
python -c "
import pandas as pd
original = pd.read_csv('logs/original_grades.csv')
resubmit = pd.read_csv('logs/grading_summary.csv')
combined = pd.merge(original, resubmit, on='student_folder', suffixes=('_orig', '_resub'))
combined['final_grade'] = combined[['grade_orig', 'grade_resub']].max(axis=1)
combined[['student_folder', 'grade_orig', 'grade_resub', 'final_grade']].to_csv('logs/final_grades.csv', index=False)
"
```

---

## Custom Grading Workflows

### Scenario 1: Peer Review Instead of Grading

**Problem:** Want detailed feedback, not numeric grades.

**Solution - Modify grading key for feedback mode:**

```text
# feedback_key.txt

Please provide constructive peer review feedback on this submission.

For each aspect, comment on:
1. What was done well
2. What could be improved
3. Specific suggestions for improvement

Aspects to review:
- Code organization and structure
- Naming conventions and readability
- Comments and documentation
- Error handling
- Best practices adherence
- Potential bugs or issues

Format your feedback as a detailed review letter to help the student improve.

DO NOT assign numeric scores. Focus on constructive feedback.
```

**Configuration:**

```json
{
  "assignment_pattern": "student_*",
  "grading_key_file": "feedback_key.txt",
  "required_files": ["**/*.py"],
  "max_score": 0,
  "language_profile": ["python"]
}
```

**Run:**

```bash
repo-grading-assistant --config feedback_config.json
```

Students receive `grade_summary.txt` with detailed feedback but no numeric grade.

---

### Scenario 2: Security Review Pass

**Problem:** Want to check for security issues before grading functionality.

**Solution - Two-pass grading:**

**Pass 1: Security Review**

```text
# security_key.txt

Review this code ONLY for security vulnerabilities. Identify:

1. SQL injection risks
2. Cross-site scripting (XSS) vulnerabilities
3. Authentication/authorization issues
4. Sensitive data exposure
5. Insecure cryptography
6. Input validation problems
7. Dependency vulnerabilities

For each issue found, provide:
- Severity (Critical/High/Medium/Low)
- Location in code
- Explanation of the risk
- Suggested fix

Do not assess functionality or assign points. Focus only on security.
```

```bash
repo-grading-assistant --config security_review_config.json
# Creates security reports in each student folder
```

**Pass 2: Functionality Grading**

```bash
# After reviewing security issues with students
repo-grading-assistant --config normal_grading_config.json
```

---

### Scenario 3: Tiered Evaluation (Basic → Advanced)

**Problem:** Want to evaluate basic requirements first, then advanced features.

**Solution:**

**Step 1: Basic evaluation**

```json
// basic_config.json
{
  "grading_key_file": "basic_requirements.txt",
  "required_files": ["main.py", "README.md"],
  "max_score": 40
}
```

```bash
repo-grading-assistant --config basic_config.json
mv logs/grading_summary.csv logs/basic_grades.csv
```

**Step 2: Advanced evaluation**

```json
// advanced_config.json
{
  "grading_key_file": "advanced_features.txt",
  "required_files": ["**/*.py"],
  "max_score": 20
}
```

```bash
repo-grading-assistant --config advanced_config.json
mv logs/grading_summary.csv logs/advanced_grades.csv
```

**Step 3: Combine**

```python
import pandas as pd
basic = pd.read_csv('logs/basic_grades.csv')
advanced = pd.read_csv('logs/advanced_grades.csv')
combined = pd.merge(basic, advanced, on='student_folder', suffixes=('_basic', '_advanced'))
combined['total_grade'] = combined['grade_basic'] + combined['grade_advanced']
combined.to_csv('logs/final_grades.csv', index=False)
```

---

## Managing Multiple Assignments

### Organized Directory Structure

```
grading/
├── lab3/
│   ├── config.json
│   ├── keys/
│   │   └── lab3_key.txt
│   ├── students/
│   │   ├── student_1/
│   │   └── student_2/
│   └── logs/
│       └── grading_summary.csv
├── lab4/
│   ├── config.json
│   ├── keys/
│   │   └── lab4_key.txt
│   ├── students/
│   └── logs/
└── lab5/
    ├── config.json
    ├── keys/
    ├── students/
    └── logs/
```

### Grade All Assignments Script

```bash
#!/bin/bash
# grade_all.sh

for lab in lab3 lab4 lab5; do
  echo "=== Grading $lab ==="
  cd $lab
  
  repo-grading-assistant \
    --config config.json \
    --repo-root students
  
  cd ..
  echo "=== $lab complete ==="
  echo
done

echo "All assignments graded!"
```

---

## Integration with LMS

### Export to Canvas/Blackboard Format

```python
# export_to_lms.py
import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Usage: python export_to_lms.py <csv_file>")
    sys.exit(1)

df = pd.read_csv(sys.argv[1])

# Canvas format: Student ID, Assignment, Score, Comments
# Assuming student folder names are student IDs
canvas_export = pd.DataFrame({
    'Student ID': df['student_folder'],
    'Assignment': 'Lab 5',  # Set appropriately
    'Score': df['grade'],
    'Max Points': df['max_score'],
    'Comments': df['evaluation_notes']
})

canvas_export.to_csv('canvas_import.csv', index=False)
print("Canvas import file created: canvas_import.csv")
```

**Usage:**

```bash
repo-grading-assistant --config my_config.json
python export_to_lms.py logs/grading_summary.csv
# Upload canvas_import.csv to your LMS
```

---

## Advanced Configuration

### Dynamic Configuration Generation

**Problem:** Need to grade 20 similar assignments with slightly different configs.

**Solution - Generate configs programmatically:**

```python
# generate_configs.py
import json

template = {
    "required_files": ["**/*.py", "README.md"],
    "max_score": 60,
    "language_profile": ["python"],
    "exclusions": []
}

for i in range(3, 8):  # Labs 3-7
    config = template.copy()
    config["assignment_pattern"] = f"lab{i}_*"
    config["grading_key_file"] = f"keys/lab{i}_key.txt"
    
    with open(f"lab{i}/config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Created lab{i}/config.json")
```

---

### Environment-Specific Configurations

```bash
# Use different configs for different environments

# Development (use cheaper model, less output)
export GRADING_ENV=dev
repo-grading-assistant --config config_dev.json

# Production (use best model, full detail)
export GRADING_ENV=prod
repo-grading-assistant --config config_prod.json
```

---

## Tips and Best Practices

### 1. Always Backup Before Re-grading

```bash
backup_grading_results() {
  timestamp=$(date +%Y%m%d_%H%M%S)
  mkdir -p backups/$timestamp
  cp -r logs backups/$timestamp/
  find . -name "grade_summary.txt" -exec cp --parents {} backups/$timestamp/ \;
  echo "Backup created: backups/$timestamp"
}

# Use before re-grading
backup_grading_results
repo-grading-assistant --config my_config.json
```

### 2. Validate Before Full Run

```bash
# Always test with one student first
repo-grading-assistant --config my_config.json --validate

# Check the output
cat student_1/grade_summary.txt
```

### 3. Monitor API Costs

```bash
# Log API calls for cost tracking
repo-grading-assistant --config my_config.json 2>&1 | tee api_usage.log

# Count API calls
grep "API call" api_usage.log | wc -l
```

### 4. Version Control Your Configurations

```bash
git add configs/ keys/
git commit -m "Lab 5 grading configuration"
git tag lab5_grading_v1
```

---

## Troubleshooting Advanced Scenarios

### Issue: Inconsistent grades across re-runs

**Cause:** AI models have some randomness.

**Solution:** The default `temperature=1` may cause variation. For more consistent results, create a custom global config:

```json
{
  "model": "gpt-5-mini",
  "temperature": 0.3
}
```

Note: gpt-5-mini only supports temperature=1, so this may require using a different model.

---

### Issue: Very large student repositories slow down grading

**Cause:** Too many files being read and sent to API.

**Solution:** Aggressive exclusions

```json
{
  "exclusions": [
    "node_modules",
    "__pycache__",
    ".git",
    "*.pyc",
    "build",
    "dist",
    "venv",
    ".venv",
    "*.min.js",
    "*.min.css",
    "images",
    "media"
  ]
}
```

---

## Next Steps

- [ARCHITECTURE.md](ARCHITECTURE.md) - Understand internal workings
- [EXAMPLES_WALKTHROUGH.md](EXAMPLES_WALKTHROUGH.md) - Basic usage guide  
- [FAQ](../README.md#faq) - Common questions
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribute improvements

---

**Have an advanced use case not covered here?** Open an issue or discussion on GitHub to share your workflow!
