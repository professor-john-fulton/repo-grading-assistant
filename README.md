README.md

# Repo Grading Assistant

Assists automates rubric-based grading of GitHub/GitLab student repositories with auditable AI feedback.

---

## Overview

The **Repo Grading Assistant** scans a folder of student repositories, collects required submission files, submits their contents for evaluation using an instructor-defined grading template, and produces both per-student feedback and an aggregate CSV summary.

The system is designed to be:

- Configuration-driven  
- Prompt-extensible  
- Resume-safe  
- Auditable  
- Open-source friendly  

---

## Requirements

- Python 3.11+
- OpenAI API key
- Windows, macOS, or Linux

---

## Installation

> **Note (Git Bash users):**  
> The following activation command uses `source`, which only works in **Git Bash**.  
> If you are using **PowerShell (Windows default)**, activate with:
> ```
> .\.venv\Scripts\Activate.ps1
> ```


```bash
git clone https://github.com/professor-john-fulton/repo-grading-assistant.git 
cd repo-grading-assistant 
py -3.11 -m venv .venv 
source .venv/Scripts/activate 
python -m pip install -U pip 
python -m pip install -e ".[dev]" 
repo-grading-assistant.exe --help
```


### Windows

```bash
setx OPENAI_API_KEY "your-key-here"
```
### macOS/Linux

```bash
export OPENAI_API_KEY="your-key-here"
```

## Quick Start

### Dry Run (no API calls)

```bash
repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --dry-run
```
### Validate Configuration

```bash
repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  \
  --validate 
```
### Run Full Grading

```bash
repo-grading-assistant \
  --config docs/examples/grading_config_example.json  \
  --repo-root docs/examples/grading_assignment_example  
```

## Configuration Format

Each assignment uses a JSON configuration file.

### Example
```json

{
  "assignment_pattern": "lab-5-*",
  "grading_key_file": "Lab05-key.txt",
  "required_files": ["models.py", "views.py", "*.css"],
  "max_score": 60,
  "language_profile": ["python", "web"],
  "exclusions": []
}
```

### Fields

Field	Purpose

  - assignment_pattern -	Pattern for identifying student directories
  - grading_key_file	- Assignment grading template
  - required_files	- Files or global patterns with optional cardinality constraints with fallback to filename discovery if paths do not exist. Wildcards are evaluated using true global patterns (**, *, ?), not simple suffix checks.
  - max_score - score for this assignment if there are no deductions
  - language_profile - contaions "standard" exclusions (ignored, ungraded files and directories) for various languages/environments
  - exclusions	- additional Files/directories to ignore in scoring


## Output Files

### Student Report
```bash

<student_folder>/grade_summary.txt
```

### CSV Summary
```bash
logs/grading_summary.csv
```
### Execution Log
```bash

logs/grading.log
```

## Prompt System
Prompts are externalized in seperate files:

### ComponentLocation
  - System behavior	 - AI Prompt - one prompt for all grading
      - prompts/base_system_prompt.txt
  - Assignment grading	- one key for each assignment
      - keys/*.txt

The engine builds each prompt dynamically using:

  - System prompt

  - Assignment template

  - Student submission

## Troubleshooting
|Issue	|Fix|
--- | --- | 
|Prompt not found	|Confirm prompts/base_system_prompt.txt exists|
|API key error	|Verify OPENAI_API_KEY is set|
|No repos found	|Check assignment_pattern|
|CSV not created	|Check write permissions|
|Rule violations  |Check cardinality ranges or wildcard patterns|
|  |  |



## Command Line Options
```bash
repo-grading-assistant --help
```

REQUIRED OPTIONS:
  --config
  --repo-root


|Option | Definition|
--- | --- |
|  -h, --help            |show this help message and exit|
|  --version             |show program's version number and exit|
 | --config CONFIG       |Path to configuration JSON. REQUIRED|
|  --repo-root REPO_ROOT|Path to the folder containing all student repositories. REQUIRED|
|  --dry-run             |List/check without API calls.Useful for verifying configuration and prompt behavior before running a full grading batch. No grade_summary.txt files are written in dry-run mode.|
|  --validate           | Verify configuration, key file, and API key, then grade ONLY the first matching student repository. Useful for testing before a full run.|
|  --skip-scored         |Skip any student directory that already contains grading_summary.txt|
|  --student STUDENT     |Only grade the specified student directory. Exact directory name match (case-insensitive).|
|  --system-prompt SYSTEM_PROMPT|Path to system-level grading prompt file.|


------------------------------------------------------------
OUTPUT FILES
------------------------------------------------------------

grading_summary.txt
  - Written inside each student repository after grading.

logs/grading.log
  - Execution log file for troubleshooting.

logs/grading_summary.csv
  - Consolidated grading report with one row per student.


------------------------------------------------------------
EXAMPLE USAGE
------------------------------------------------------------

Dry run (safe test):

- repo-grading-assistant --config configs/lab5.json --repo-root D:/Submissions --dry-run

Validate one student:
- repo-grading-assistant --config configs/lab5.json --repo-root D:/Submissions --validate

Full grading run:
- repo-grading-assistant --config configs/lab5.json --repo-root D:/Submissions


------------------------------------------------------------
CONFIGURATION FILE SETTINGS  (JSON)
------------------------------------------------------------
{
  "assignment_pattern": "homework-5-*",
      # Glob pattern for student submission folders.
      # Example: "lab-3-*", "homework-5-*"

  "grading_key_file": "Homework05-key.docx",
      # Path to the answer key or rubric file used for scoring.
      # May be DOCX or TXT; content will be read as text.
      # Each requirement to be scored should be marked "*** +3 points"

  "required_files": [
      "src/index.js",
      "src/contacts.js",
      "src/components/App.jsx",
      "src/components/Card.jsx",
      "public/index.html",
      "public/styles.css"
  ],
      # List of relative paths expected within each student folder.
      # The script allows small filename variations (e.g., style.css vs. styles.css).


}

## Cardinality Rules

Required files may specify how many matches are allowed using parentheses:

filename(min..max)


Examples:

|Rule	|Meaning |
--- | --- | 
|urls.py(2)|Expect exactly 2 files named urls.py|
|README.md(0..1)|Optional|
|*.png(0..*)|Any number allowed|
|config.json(1..3)|Between 1 and 3|



If no count is provided, exactly one file is required by default.

File matching is recursive and directory-agnostic.

Add example config:
```bash
"required_files": [
  "urls.py(0..2)",
  "models.py",
  "*.png(0..*)"
]
```

## Documentation

- Testing: `docs/testing.md`

---

## License

This project is open-source.  
MIT License

---

## Contributing

See `CONTRIBUTING.md` for development guidelines.

## Security
## Data Privacy
## Roadmap
## Support
## Citation
