
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

**Quick Links:**
- 📖 [Examples Walkthrough](docs/EXAMPLES_WALKTHROUGH.md) - Step-by-step guide with sample data
- ❓ [FAQ](#faq) - Common questions and troubleshooting
- 🚀 [Quickstart Guide](QUICKSTART.md) - Get started in 5 minutes

---

## Requirements

- Python **3.11+**
- OpenAI API key
- Windows
  - Likely usable in macOS, or Linux, but untested

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

For local development, create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

> **Note:** The `.env` file is excluded from git by `.gitignore` to keep your API key secure.
>
> **For remote deployments:** Use your platform's environment variable configuration (e.g., Railway, Heroku, etc.) instead of a `.env` file.

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
| model | (Optional) OpenAI model to use for this assignment |

---

## Model Configuration

This tool uses OpenAI's API to evaluate student code. You can configure which model to use at three levels:

### Model Selection Priority (highest to lowest):

1. **Assignment Config** - Set `"model"` in your assignment's JSON config file
2. **Global Config** - Set `"model"` in `configs/global_config.json`
3. **Default Fallback** - Uses `gpt-5-mini` if nothing is specified

### Example Global Config (`configs/global_config.json`):

```json
{
  "model": "gpt-5-mini"
}
```

### Example Assignment Config with Model Override:

```json
{
  "assignment_pattern": "lab-5-*",
  "grading_key_file": "Lab05-key.txt",
  "required_files": ["models.py", "views.py"],
  "max_score": 60,
  "model": "gpt-5"
}
```

### Available Models

Common OpenAI models (as of January 2026):
- `gpt-5-mini` - Fast, cost-efficient (default)
- `gpt-5` - More capable, higher cost
- `gpt-5-nano` - Fastest, most cost-efficient
- `gpt-4.1` - Previous generation
- `gpt-4o-mini` - Legacy fast model

See https://platform.openai.com/docs/models for the full list.

### Important: API Key Model Access

⚠️ **Your OpenAI API key must have access to the model you select.** If your API key doesn't have permission for a specific model, you'll receive an error:

```
Error: The API project does not have access to model gpt-5-mini
```

**To grant model access:**
1. Go to https://platform.openai.com/
2. Navigate to your project settings
3. Find model permissions/limits (location varies)
4. Enable the models you need

> **Developer Note:** Finding the correct settings page for model permissions in OpenAI's dashboard can be challenging. If you have difficulty locating these settings, consider using ChatGPT to help navigate to the right configuration page, or contact OpenAI support.

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
| System behavior | `src/repo_grading_assistant/data/base_system_prompt.txt` (packaged) |
| Assignment (grading) keys | Specified in config, typically in `./keys/` directory |

The engine builds prompts dynamically using:

- System prompt  
- Assignment template  
- Student submission  

---

## Troubleshooting

| Issue | Fix |
|------|-----|
| Prompt not found | Ensure package is installed correctly: `python -m pip install -e .` |
| API key error | Verify `.env` file exists with `OPENAI_API_KEY` set |
| Model access error | Verify your OpenAI API key has access to the model (see model configuration below) |
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

See `SECURITY.md` for information on reporting security vulnerabilities.

---

## Data Privacy

This tool processes student code locally and sends it to OpenAI's API for evaluation. Key privacy considerations:

- **Local Processing:** Student repositories remain on your local machine
- **API Transmission:** Code excerpts are sent to OpenAI for grading feedback
- **No Cloud Storage:** This tool does not store data in any cloud service
- **Logs:** Execution logs are stored locally in `logs/` directory
- **API Key Security:** Keep your `.env` file secure and never commit it to version control

**Best Practices:**
- Review OpenAI's data usage policy: https://openai.com/policies/privacy-policy
- Inform students that their code may be processed by AI for grading
- Ensure compliance with your institution's data privacy policies
- Do not commit student submissions, grade outputs, or logs to version control

---

## FAQ

### General Questions

**Q: How much does it cost to grade an assignment?**

A: Costs depend on code size and student count. Typical costs with gpt-5-mini:
- **Small assignment** (calculator, basic web form): ~$0.001-0.003 per student
- **Medium assignment** (full Django/Flask app): ~$0.005-0.015 per student
- **Large assignment** (complex multi-file project): ~$0.020-0.050 per student

For a class of 30 students with medium-sized assignments: ~$0.15-0.45 total.

**Tip:** Use `exclusions` to skip unnecessary files (node_modules, build artifacts, etc.) to reduce costs.

**Q: Can I use this for non-Python code?**

A: Yes! While the examples show Python/Django, the tool works with any programming language. The AI model understands all major languages including:
- JavaScript/TypeScript (React, Node.js, etc.)
- Java (Spring Boot, Android, etc.)
- C/C++/C#
- Ruby (Rails, etc.)
- PHP (Laravel, etc.)
- Go, Rust, Swift, Kotlin, and more

Set the `language_profile` in your config to help the AI understand context (e.g., `["javascript", "react"]`).

**Q: Can I grade Jupyter notebooks?**

A: Yes! Include `**/*.ipynb` in your `required_files` or let the default glob patterns find them. The AI can read and evaluate Jupyter notebook JSON structure, understanding both code cells and markdown explanations.

**Q: What if students have different folder structures?**

A: Use flexible glob patterns:
- `**/filename.py` - finds file at any level
- `**/*.py` - finds all Python files anywhere
- Remove strict path requirements from `required_files`

The AI evaluates based on functionality and code quality, not folder structure. Missing required files are noted in the report but grading still proceeds.

**Q: How accurate is the AI grading?**

A: The AI is highly effective for:
- Code structure and organization evaluation
- Feature implementation verification
- Best practices assessment
- Partial credit decisions

**Recommendation:** Spot-check 10-20% of grades initially, especially borderline cases. Once confident in the grading key and AI consistency, reduce manual review.

**Q: Can students dispute their grades?**

A: Yes. The `grade_summary.txt` file explains the reasoning for each point awarded or deducted. You can:
1. Review the AI's evaluation with the student
2. Manually adjust the grade if the AI missed something
3. Refine your grading key for future assignments
4. Re-run grading with updated instructions

### Grading Keys & Templates

**Q: How detailed should my grading key be?**

A: More specific keys yield more consistent results. Compare:

**Too vague:**
```text
- Good code quality
*** +20 points
```

**Better:**
```text
- Code quality assessment:
  * Proper function/class naming conventions
  * Adequate comments for complex logic
  * No code duplication (DRY principle)
  * Appropriate use of data structures
*** +20 points (partial credit for incomplete)
```

**Q: How do I handle bonus points?**

A: Mark bonus items explicitly in your grading key:

```text
*** +5 bonus points (above the max_score)
```

Set `max_score` in config to the base points total (not including bonuses). The AI will:
- Award up to `max_score` for base requirements
- Add bonus points on top for stretch goals
- Report as "68/60 (+8 bonus)" for clarity

**Q: Can I grade subjective criteria like "code elegance"?**

A: Yes, but provide clear guidelines:

```text
- Code elegance (subjective assessment):
  * Uses idiomatic language patterns
  * Avoids unnecessary complexity
  * Well-organized with logical flow
  * Professional formatting and style
*** +10 points (partial credit encouraged)
```

The AI is good at subjective assessment when given context and examples.

### Technical Issues

**Q: Why is grading slow?**

A: Each student requires an API call to OpenAI. For 30 students:
- Expected time: ~1-3 minutes total
- API rate limits may add delays

**Tip:** Use `--validate` flag to test with first student only before processing entire class.

**Q: What if the API call fails for one student?**

A: The tool continues processing other students and logs the error. You can re-run with `--student <folder_name>` to grade just the failed student.

**Q: Can I use a different AI model?**

A: Yes! Specify in your config:

```json
{
  "model": "gpt-4",
  "max_tokens": 2000
}
```

Or set globally in `configs/global_config.json`. See [Model Configuration](#model-configuration) for details.

**Q: How do I exclude build files or dependencies?**

A: Use the `exclusions` field in your config:

```json
{
  "exclusions": [
    "node_modules",
    "__pycache__",
    "*.pyc",
    ".venv",
    "build",
    "dist",
    ".git"
  ]
}
```

This reduces API costs and focuses evaluation on student code.

### Best Practices

**Q: Should I tell students their code will be AI-graded?**

A: Yes, transparency is important:
- Inform students in the syllabus or assignment instructions
- Explain that AI provides consistent, detailed feedback
- Emphasize that you review results and can override decisions
- Note that the AI sees their code (privacy consideration)

**Q: How often should I review AI grading decisions?**

A: Recommended approach:
1. **First assignment:** Review 100% of grades to validate grading key
2. **Second assignment:** Review ~30% (focus on borderline grades)
3. **Ongoing:** Review ~10-20% per assignment, plus any student disputes

**Q: Can I use this for peer review instead of grading?**

A: Yes! Modify your grading key to provide feedback format:

```text
Provide constructive feedback on:
- What the student did well
- Areas for improvement
- Specific suggestions for better code organization
- Security or performance concerns

Do not assign numerical grades.
```

Run with `max_score: 0` to generate feedback reports without scores.

---

## Support

For questions, issues, or feature requests:

- **Issues:** https://github.com/professor-john-fulton/repo-grading-assistant/issues
- **Discussions:** Open an issue with the "question" label
- **Email:** john.fulton2@franklin.edu

This is a community project maintained by volunteers. Response times may vary.

---

## Citation

If you use this tool in academic work, please cite:

```
Fulton, J. (2026). Repo Grading Assistant: AI-Assisted Rubric-Based 
Code Evaluation Tool (Version 0.1.0) [Computer software]. 
https://github.com/professor-john-fulton/repo-grading-assistant
```

BibTeX:
```bibtex
@software{fulton2026repogradingassistant,
  author = {Fulton, John},
  title = {Repo Grading Assistant: AI-Assisted Rubric-Based Code Evaluation Tool},
  year = {2026},
  url = {https://github.com/professor-john-fulton/repo-grading-assistant},
  version = {0.1.0}
}
```
