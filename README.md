
<!-- README.md -->

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![CI](https://github.com/professor-john-fulton/repo-grading-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/professor-john-fulton/repo-grading-assistant/actions/workflows/ci.yml)
![Platform](https://img.shields.io/badge/tested%20on-windows-blue)

# Repo Grading Assistant

Assists rubric-based grading of GitHub/GitLab student repositories with auditable AI feedback.

---

## Overview

**Repo Grading Assistant** scans a folder of student repositories, collects required submission files, evaluates them using an instructor-defined grading template, and produces:

- Per-student feedback reports  
- A consolidated CSV grading summary  

The system is designed to be:

- **Configuration-driven**  
- **Prompt-extensible**  
- **Resume-safe**  
- **Auditable**  
- **Open-source friendly**

---

## Requirements

- Python **3.11+**
- OpenAI API key
- Windows
  - Likley usable in macOS, or Linux, but untested

---

## Installation

### Windows (Git Bash)

```bash
git clone https://github.com/professor-john-fulton/repo-grading-assistant.git
cd repo-grading-assistant

py -3.11 -m venv .venv
source .venv/Scripts/activate

python -m pip install -U pip
python -m pip install -e ".[dev]"

repo-grading-assistant.exe --help
```

> **Note:** These commands are for **Git Bash**.  
> If you are using PowerShell, follow the instructions below.

---

### Windows (PowerShell)

```powershell
git clone https://github.com/professor-john-fulton/repo-grading-assistant.git
cd repo-grading-assistant

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -U pip
python -m pip install -e ".[dev]"

repo-grading-assistant --help
```

---

### Set API Key

#### Windows
```powershell
setx OPENAI_API_KEY "your-key-here"
```

#### macOS / Linux
```bash
export OPENAI_API_KEY="your-key-here"
```

---

## Quick Start

### Dry Run (no API calls)

```bash
repo-grading-assistant   --config docs/examples/grading_config_example.json   --repo-root docs/examples/grading_assignment_example   --dry-run
```

### Validate Configuration

```bash
repo-grading-assistant   --config docs/examples/grading_config_example.json   --repo-root docs/examples/grading_assignment_example   --validate
```

### Run Full Grading

```bash
repo-grading-assistant   --config docs/examples/grading_config_example.json   --repo-root docs/examples/grading_assignment_example
```

---

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

| Field | Purpose |
|------|--------|
| assignment_pattern | Pattern for identifying student directories |
| grading_key_file | Assignment grading template |
| required_files | Files or wildcard patterns with optional cardinality |
| max_score | Base assignment score |
| language_profile | Loads standard exclusions by language |
| exclusions | Additional files/directories to ignore |

---

## Output Files

### Student Report
```
<student_folder>/grade_summary.txt
```

### CSV Summary
```
logs/grading_summary.csv
```

### Execution Log
```
logs/grading.log
```

---

## Prompt System

Prompts are externalized:

| Component | Location |
|------------|-----------|
| System behavior | `prompts/base_system_prompt.txt` |
| Assignment (grading) keys | `keys/*.txt` |

The engine builds prompts dynamically using:

- System prompt  
- Assignment template  
- Student submission  

---

## Troubleshooting

| Issue | Fix |
|------|-----|
| Prompt not found | Confirm `prompts/base_system_prompt.txt` exists |
| API key error | Verify `OPENAI_API_KEY` is set |
| No repos found | Check `assignment_pattern` |
| CSV not created | Check write permissions |
| Rule violations | Check cardinality or wildcard rules |

---

## Command Line Options

```bash
repo-grading-assistant --help
```

| Option | Description |
|--------|-------------|
| --config | Path to configuration JSON (required) |
| --repo-root | Root folder containing student repos |
| --dry-run | Validate without API calls |
| --validate | Grade first repo only |
| --skip-scored | Skip folders with existing results |
| --student | Grade a single student |
| --system-prompt | Custom system prompt path |

---

## Cardinality Rules

Rules support quantity constraints:

| Rule | Meaning |
|------|--------|
| urls.py(2) | Exactly 2 files |
| README.md(0..1) | Optional  (zero or one file)|
| *.png(0..*) | Any number  (zero or more files)|
| config.json(1..3) | Between 1 and 3 |

Default: **exactly one** file.

---

## Documentation

- Testing: `docs/testing.md`

---

## License

MIT License

---

## Contributing

See `CONTRIBUTING.md`

---

## Security  
## Data Privacy  
## Roadmap  
## Support  
## Citation  
