# Architecture Documentation

This document explains the internal structure and operation of the Repo Grading Assistant.

---

## System Overview

The Repo Grading Assistant is a Python CLI tool that automates code evaluation by:

1. **Scanning** student repository folders
2. **Collecting** required files based on patterns
3. **Assembling** evaluation prompts with context
4. **Calling** OpenAI API for intelligent assessment
5. **Generating** detailed reports and CSV summaries

```
┌─────────────────────────────────────────────────────────────┐
│                     User Input                               │
│  - Configuration JSON                                        │
│  - Grading Key (rubric)                                      │
│  - Student Repository Folder                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Configuration Loader                            │
│  - Parse JSON config                                         │
│  - Load grading key file                                     │
│  - Load global config (if exists)                            │
│  - Determine model & parameters                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Repository Scanner                                │
│  - Match student folders by pattern (glob)                   │
│  - Validate folder structure                                 │
│  - Filter by --student flag if specified                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
          ┌──────────┴──────────┐
          │  For Each Student   │
          └──────────┬──────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│             File Collection Engine                           │
│  - Match required_files patterns                             │
│  - Apply exclusions (by language profile + custom)           │
│  - Validate cardinality rules                                │
│  - Read file contents                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│             Prompt Assembly                                  │
│  1. Load base system prompt (packaged)                       │
│  2. Add grading key (rubric) content                         │
│  3. Add student file contents with structure                 │
│  4. Include metadata (max_score, bonus points, etc.)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenAI API Call                                 │
│  - Model: configurable (default gpt-5-mini)                  │
│  - Messages: system + user prompt                            │
│  - Error handling: retries, auth, rate limits                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Response Processing                                │
│  - Parse structured evaluation                               │
│  - Extract score, bonus points                               │
│  - Extract reasoning for each requirement                    │
│  - Identify missing files                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Output Generation                               │
│  - Write <student>/grade_summary.txt                         │
│  - Append logs/grading_summary.csv                           │
│  - Log execution details                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Package Structure

```
src/repo_grading_assistant/
├── __init__.py                    # Package initialization
├── cli.py                         # Command-line interface entry point
├── grade_assignments.py           # Core grading engine (main module)
└── data/
    └── base_system_prompt.txt     # Default AI system instructions

docs/
├── ARCHITECTURE.md                # This file
├── EXAMPLES_WALKTHROUGH.md        # Step-by-step guide
├── testing.md                     # Testing documentation
└── examples/                      # Sample data for testing
    ├── grading_config_example.json
    ├── grading_key_example.txt
    └── grading_assignment_example/
        ├── student_1/
        └── student_2/

tests/
├── conftest.py                    # Pytest fixtures
└── test_grade_assignments.py      # Unit & integration tests

configs/
└── global_config.json             # Global settings (model, params)

logs/
├── grading.log                    # Execution log (auto-generated)
└── grading_summary.csv            # CSV output (auto-generated)
```

---

## Core Components

### 1. Configuration System

**Files:** `grade_assignments.py` (load_config, merge_global_config)

**Purpose:** Manages multi-level configuration hierarchy

**Configuration Priority:**
1. Command-line arguments (highest)
2. Assignment-specific config JSON
3. Global config (`configs/global_config.json`)
4. Hardcoded defaults (lowest)

**Example Configuration Flow:**

```python
# Step 1: Load assignment config
assignment_config = load_config("my_assignment.json")
# → {"assignment_pattern": "student_*", "max_score": 60}

# Step 2: Merge with global config
global_config = load_config("configs/global_config.json")
# → {"model": "gpt-5-mini", "max_tokens": 2000}

# Step 3: Combine (assignment overrides global)
final_config = {**global_config, **assignment_config}
# → {"model": "gpt-5-mini", "assignment_pattern": "student_*", ...}
```

**Key Fields:**
- `assignment_pattern`: Glob for student folders
- `grading_key_file`: Path to rubric
- `required_files`: List of file patterns with optional cardinality
- `max_score`: Base points (before bonus)
- `language_profile`: Loads preset exclusions
- `exclusions`: Additional patterns to ignore
- `model`: OpenAI model name
- `max_tokens`: Response length limit

---

### 2. File Collection Engine

**Files:** `grade_assignments.py` (find_repos, collect_required_files, should_exclude)

**Purpose:** Discovers and reads student code files

**Process:**

```python
# 1. Find student repositories
repos = find_repos(
    repo_root="./assignments",
    pattern="student_*"
)
# → [Path("student_1"), Path("student_2"), ...]

# 2. For each repo, collect required files
for repo_path in repos:
    files = collect_required_files(
        repo_path=repo_path,
        required_patterns=["**/*.py", "README.md"],
        exclusions=["__pycache__", "*.pyc"]
    )
    # → {"main.py": "content...", "utils.py": "content..."}
```

**Pattern Matching:**
- Uses Python `glob.glob()` for file discovery
- Supports `**` for recursive matching
- Applies exclusions before collection

**Exclusion System:**
- Language profiles load preset exclusions:
  - `python`: `["__pycache__", "*.pyc", ".pytest_cache", ".venv"]`
  - `web`: `["node_modules", "bower_components", "dist", "build"]`
- Custom exclusions from config merge with presets
- Exclusions use `fnmatch` for pattern matching

---

### 3. Cardinality Rules Engine

**Files:** `grade_assignments.py` (parse_cardinality, validate_cardinality)

**Purpose:** Enforces file count constraints

**Syntax:**
- `filename.py` → exactly 1 file (implicit)
- `filename.py(2)` → exactly 2 files
- `filename.py(0..1)` → zero or one file (optional)
- `filename.py(0..*)` → zero or more files (any)
- `filename.py(1..3)` → between 1 and 3 files

**Parsing Logic:**

```python
def parse_cardinality(pattern: str) -> tuple[str, tuple[int, int]]:
    """
    Extract cardinality from pattern.
    
    Examples:
        "urls.py(2)" → ("urls.py", (2, 2))
        "*.txt(0..1)" → ("*.txt", (0, 1))
        "config.json" → ("config.json", (1, 1))  # default
    """
    match = re.match(r"^(.+?)\((\d+)\.\.(\*|\d+)\)$", pattern)
    if match:
        base, min_val, max_val = match.groups()
        max_count = float('inf') if max_val == '*' else int(max_val)
        return base, (int(min_val), max_count)
    
    match = re.match(r"^(.+?)\((\d+)\)$", pattern)
    if match:
        base, count = match.groups()
        return base, (int(count), int(count))
    
    return pattern, (1, 1)  # Default: exactly one
```

**Validation:**

```python
def validate_cardinality(
    pattern: str, 
    found_files: list[Path]
) -> tuple[bool, str]:
    """
    Check if found files meet cardinality requirement.
    
    Returns: (is_valid, message)
    """
    base_pattern, (min_count, max_count) = parse_cardinality(pattern)
    actual_count = len(found_files)
    
    if actual_count < min_count:
        return False, f"Expected at least {min_count} but found {actual_count}"
    if actual_count > max_count:
        return False, f"Expected at most {max_count} but found {actual_count}"
    
    return True, f"Found {actual_count} (valid)"
```

**Behavior:**
- Validation runs before grading
- Violations are logged but **don't stop grading**
- Warning included in student report
- Helps identify incomplete submissions

---

### 4. Prompt Assembly System

**Files:** `grade_assignments.py` (build_prompt, load_system_prompt)

**Purpose:** Constructs AI evaluation prompts

**Prompt Structure:**

```
┌─────────────────────────────────────────┐
│   System Prompt (Role Instructions)     │
│   - Base system behavior                │
│   - Evaluation guidelines               │
│   - Output format requirements          │
└─────────────────────────────────────────┘
            ▼
┌─────────────────────────────────────────┐
│   Grading Key (Assignment Rubric)       │
│   - Requirements with point values      │
│   - Bonus criteria                      │
│   - Specific evaluation instructions    │
└─────────────────────────────────────────┘
            ▼
┌─────────────────────────────────────────┐
│   Student Submission Context            │
│   - File structure overview             │
│   - File contents (formatted)           │
│   - Metadata (max_score, language)      │
└─────────────────────────────────────────┘
```

**Base System Prompt:**

Located in `src/repo_grading_assistant/data/base_system_prompt.txt`, this defines the AI's behavior:

- Role: Expert code reviewer and educator
- Output format: Structured evaluation
- Grading philosophy: Fair, detailed, constructive
- Partial credit guidelines
- Bonus point handling

**Dynamic Prompt Building:**

```python
def build_prompt(
    grading_key: str,
    files_content: dict[str, str],
    max_score: int,
    language_profile: list[str]
) -> str:
    """
    Assemble complete evaluation prompt.
    """
    system_prompt = load_system_prompt()
    
    # Format file contents
    files_section = ""
    for filename, content in files_content.items():
        files_section += f"\n### {filename}\n```\n{content}\n```\n"
    
    # Build complete prompt
    prompt = f"""
{system_prompt}

## Assignment Grading Key
{grading_key}

## Configuration
- Maximum Score: {max_score}
- Language Profile: {', '.join(language_profile)}

## Student Submission
{files_section}

## Instructions
Evaluate the submission against the grading key. Provide:
1. Score for each requirement with reasoning
2. Bonus points if applicable (above max_score)
3. Missing files or concerns
4. Final grade calculation
"""
    return prompt
```

---

### 5. OpenAI Integration

**Files:** `grade_assignments.py` (call_openai_api)

**Purpose:** Handles API communication with error handling

**API Call Flow:**

```python
def call_openai_api(
    prompt: str,
    model: str = "gpt-5-mini",
    max_tokens: int = 2000
) -> str:
    """
    Call OpenAI API with error handling and retries.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not set")
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=max_tokens  # gpt-5-mini parameter
        )
        
        return response.choices[0].message.content
        
    except openai.error.AuthenticationError:
        logging.error("Invalid API key")
        raise
    except openai.error.RateLimitError:
        logging.warning("Rate limit hit, retrying...")
        time.sleep(5)
        # Retry logic...
    except openai.error.InvalidRequestError as e:
        if "does not have access" in str(e):
            logging.error(f"API key lacks model access: {model}")
        raise
```

**Error Handling:**
- **Authentication errors:** Stop immediately (bad API key)
- **Rate limits:** Exponential backoff retry (3 attempts)
- **Timeout errors:** Retry with increased timeout
- **Invalid requests:** Log details and skip student
- **Network errors:** Retry with backoff

**Model Configuration:**

The tool supports multiple models through the configuration hierarchy:

1. **Assignment config:** `{"model": "gpt-5"}`
2. **Global config:** `configs/global_config.json`
3. **Default:** `gpt-5-mini`

---

### 6. Response Processing

**Files:** `grade_assignments.py` (parse_evaluation_response)

**Purpose:** Extract structured data from AI response

**Response Format Expected:**

```
REQUIREMENTS ANALYSIS
─────────────────────
✓ Authentication (15/15 points)
  - Reasoning...

✓ CRUD Operations (15/15 points)
  - Reasoning...

BONUS POINTS
────────────
✓ Commenting System (+5 bonus)
  - Reasoning...

FINAL GRADE: 65/60
(Base: 60, Bonus: +5)
```

**Parsing Logic:**

```python
def parse_evaluation_response(response: str) -> dict:
    """
    Extract grade and metadata from AI response.
    
    Returns:
        {
            "grade": 65,
            "max_score": 60,
            "bonus": 5,
            "evaluation_text": "...",
            "missing_files": []
        }
    """
    # Extract grade using regex
    grade_match = re.search(r"FINAL GRADE:\s*(\d+)/(\d+)", response)
    if grade_match:
        grade, max_score = map(int, grade_match.groups())
    
    # Calculate bonus
    bonus = max(0, grade - max_score)
    
    return {
        "grade": grade,
        "max_score": max_score,
        "bonus": bonus,
        "evaluation_text": response,
        "missing_files": []  # Populated from file collection
    }
```

---

### 7. Output Generation

**Files:** `grade_assignments.py` (write_grade_summary, write_csv_row)

**Purpose:** Generate student reports and consolidated summary

**Student Report (`<student>/grade_summary.txt`):**

```
================================================================================
Student: student_2
Grade: 68 out of 60 (Max: 60, Bonus: +8)
Evaluation Date: 2026-01-28T15:30:45
================================================================================

[Full AI evaluation text with reasoning]

================================================================================
```

**CSV Summary (`logs/grading_summary.csv`):**

```csv
student_folder,grade,max_score,bonus_points,timestamp,missing_required_files,evaluation_notes
student_1,60,60,0,2026-01-28T15:30:30,"","All requirements met"
student_2,68,60,8,2026-01-28T15:30:45,"","Excellent with bonus features"
```

**Generation Process:**

```python
def write_outputs(student_name: str, result: dict):
    """Write both individual report and CSV row."""
    
    # 1. Student report
    report_path = Path(student_name) / "grade_summary.txt"
    report_path.write_text(
        format_student_report(result),
        encoding="utf-8"
    )
    
    # 2. CSV row (append mode)
    csv_path = Path("logs/grading_summary.csv")
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            student_name,
            result["grade"],
            result["max_score"],
            result["bonus"],
            datetime.now().isoformat(),
            ",".join(result["missing_files"]),
            result["evaluation_notes"]
        ])
```

---

## Data Flow Example

Let's trace a complete evaluation:

### Input

**Config (`lab5_config.json`):**
```json
{
  "assignment_pattern": "student_*",
  "grading_key_file": "lab5_key.txt",
  "required_files": ["**/models.py", "**/views.py", "**/urls.py(2)"],
  "max_score": 60,
  "language_profile": ["python", "web"]
}
```

**Grading Key (`lab5_key.txt`):**
```
- Authentication system
*** +15 points

- CRUD operations
*** +15 points

Bonus: User profiles
*** +5 bonus points
```

**Student Folder:**
```
student_alice/
├── blog/
│   ├── models.py
│   ├── views.py
│   └── urls.py
└── myproject/
    └── urls.py
```

### Processing Steps

**1. Configuration Loading:**
```python
config = load_config("lab5_config.json")
# → {"assignment_pattern": "student_*", "max_score": 60, ...}

global_config = load_config("configs/global_config.json")
# → {"model": "gpt-5-mini"}

config = {**global_config, **config}
```

**2. Repository Discovery:**
```python
repos = find_repos(repo_root=".", pattern="student_*")
# → [Path("student_alice"), Path("student_bob"), ...]
```

**3. File Collection (for student_alice):**
```python
files = collect_required_files(
    repo_path="student_alice",
    patterns=["**/models.py", "**/views.py", "**/urls.py(2)"],
    exclusions=["__pycache__", "node_modules"]
)
# → {
#     "blog/models.py": "class Post(models.Model): ...",
#     "blog/views.py": "def post_list(request): ...",
#     "blog/urls.py": "urlpatterns = [...]",
#     "myproject/urls.py": "urlpatterns = [...]"
# }

# Cardinality check
validate_cardinality("**/urls.py(2)", ["blog/urls.py", "myproject/urls.py"])
# → (True, "Found 2 (valid)")
```

**4. Prompt Assembly:**
```python
prompt = build_prompt(
    grading_key=lab5_key_content,
    files_content=files,
    max_score=60,
    language_profile=["python", "web"]
)
# → Multi-part prompt with system instructions, rubric, and code
```

**5. API Call:**
```python
response = call_openai_api(
    prompt=prompt,
    model="gpt-5-mini",
    max_tokens=2000
)
# → AI evaluation text with grades and reasoning
```

**6. Response Parsing:**
```python
result = parse_evaluation_response(response)
# → {
#     "grade": 65,
#     "max_score": 60,
#     "bonus": 5,
#     "evaluation_text": "...",
#     "missing_files": []
# }
```

**7. Output Generation:**
```python
write_grade_summary("student_alice", result)
# Creates: student_alice/grade_summary.txt

write_csv_row("student_alice", result)
# Appends to: logs/grading_summary.csv
```

### Output

**`student_alice/grade_summary.txt`:**
```
================================================================================
Student: student_alice
Grade: 65 out of 60 (Max: 60, Bonus: +5)
================================================================================

✓ Authentication (15/15)
- Django authentication implemented correctly
...

✓ CRUD Operations (15/15)
- Full CRUD for blog posts
...

✓ User Profiles (+5 bonus)
- Profile page implemented with user info
...

FINAL GRADE: 65/60
```

**`logs/grading_summary.csv`:**
```csv
student_folder,grade,max_score,bonus_points,timestamp,...
student_alice,65,60,5,2026-01-28T15:30:45,...
```

---

## Extension Points

### Adding New Language Profiles

**File:** `grade_assignments.py` (LANGUAGE_EXCLUSIONS constant)

```python
LANGUAGE_EXCLUSIONS = {
    "python": ["__pycache__", "*.pyc", ".pytest_cache", ".venv"],
    "javascript": ["node_modules", "package-lock.json", "dist"],
    "java": ["target/", "*.class", ".gradle/"],
    # Add your language here:
    "rust": ["target/", "Cargo.lock"],
}
```

### Custom System Prompts

Override default prompt with `--system-prompt` flag:

```bash
repo-grading-assistant \
  --config my_config.json \
  --system-prompt custom_instructions.txt
```

### Post-Processing Hooks

The architecture supports adding custom post-processing by extending:

```python
def custom_post_process(result: dict, student_name: str) -> dict:
    """Add custom logic after AI evaluation."""
    # Example: Adjust grades based on submission time
    if is_late(student_name):
        result["grade"] *= 0.9  # 10% penalty
    return result
```

---

## Performance Considerations

### API Rate Limits

- OpenAI rate limits vary by account tier
- Tool includes exponential backoff retry logic
- For large classes (50+ students), expect ~2-5 minutes total

### Cost Optimization

**Reducing API Costs:**
1. Use aggressive exclusions (node_modules, build files)
2. Use gpt-5-mini instead of gpt-5 (cheaper)
3. Limit `max_tokens` to reasonable values (1500-2000)
4. Test with `--validate` (one student) before full run

**Typical Costs (gpt-5-mini):**
- Small assignment: $0.001-0.003 per student
- Medium assignment: $0.005-0.015 per student
- Large assignment: $0.020-0.050 per student

### Parallel Processing

Current implementation is sequential (one student at a time). Future enhancement could add parallel processing:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(grade_student, repo, config)
        for repo in repos
    ]
    results = [f.result() for f in futures]
```

**Note:** Must respect OpenAI rate limits when parallelizing.

---

## Testing Architecture

**File:** `tests/test_grade_assignments.py`

**Test Categories:**

1. **Unit Tests** - Individual function testing
   - Configuration loading
   - Pattern matching
   - Cardinality parsing
   - File exclusions

2. **Integration Tests** - Component interaction
   - End-to-end config → files → prompt flow
   - OpenAI API validation (skipped in CI)

3. **Edge Case Tests** - Boundary conditions
   - Missing config fields
   - Invalid patterns
   - Empty repositories
   - Malformed JSON

**Fixtures (`conftest.py`):**
- `temp_repo`: Creates temporary student folders
- `sample_config`: Provides test configuration
- `mock_openai`: Mocks API responses

---

## Security Considerations

### API Key Handling

- Keys loaded from `.env` file (local) or environment (production)
- Never logged or written to output files
- `.env` excluded from git via `.gitignore`

### Student Code Safety

- Code is read as text (not executed)
- No shell execution or `eval()` calls
- Files sanitized before sending to API

### Output Security

- Reports written with restricted permissions
- CSV uses proper escaping to prevent injection
- Logs exclude sensitive information

---

## Maintenance & Debugging

### Logging

All operations logged to `logs/grading.log`:

```
2026-01-28 15:30:20 - INFO - Processing student_alice
2026-01-28 15:30:21 - INFO - Found 4 files
2026-01-28 15:30:22 - INFO - API call successful
2026-01-28 15:30:23 - INFO - Grade: 65/60
```

### Dry Run Mode

Test configuration without API costs:

```bash
repo-grading-assistant --config my_config.json --dry-run
```

Validates:
- Config syntax
- File patterns
- Repository discovery
- Cardinality rules

### Validate Mode

Grade only the first student (for testing):

```bash
repo-grading-assistant --config my_config.json --validate
```

### Single Student Mode

Re-grade specific student:

```bash
repo-grading-assistant --config my_config.json --student student_alice
```

---

## Future Enhancements

Potential architecture improvements:

1. **Plugin System** - Allow custom evaluators beyond OpenAI
2. **Caching** - Cache API responses to avoid re-evaluation
3. **Parallel Processing** - Grade multiple students simultaneously
4. **Web Interface** - Browser-based configuration and review
5. **Database Backend** - Store results in SQLite/PostgreSQL
6. **Rubric Builder** - GUI for creating grading keys
7. **Student Feedback Portal** - Let students view their evaluations
8. **Version Control Integration** - Grade specific commits/branches

---

## Contributing to Architecture

When adding features:

1. **Maintain separation of concerns** - Each function has single responsibility
2. **Follow existing patterns** - Use similar error handling and logging
3. **Add tests** - Cover new functionality in test suite
4. **Update documentation** - Keep this file current
5. **Consider backwards compatibility** - Don't break existing configs

See [CONTRIBUTING.md](../CONTRIBUTING.md) for code contribution guidelines.

---

## Questions?

For architecture questions:
- Open an issue with the "question" label
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for discussion channels
- Review [EXAMPLES_WALKTHROUGH.md](EXAMPLES_WALKTHROUGH.md) for practical examples
