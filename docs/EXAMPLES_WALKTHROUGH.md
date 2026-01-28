# Examples Walkthrough

This guide walks you through grading the example assignment included in the repository, showing you exactly what to expect at each step.

## Overview

The example demonstrates grading a Django blog application assignment with:
- 2 student submissions (`student_1` and `student_2`)
- Required files validation
- Bonus points for stretch goals
- Cardinality checking (e.g., exactly 2 `urls.py` files)

**Location:** `docs/examples/grading_assignment_example/`

---

## Step 1: Examine the Assignment Structure

### Grading Key File
**File:** `docs/examples/grading_key_example.txt`

This file contains the assignment requirements with point values:

```text
Requirements:
- Authentication: Users should be able to register, login, and logout.
*** +15 points

- CRUD Operations: Users should be able to create, read, update, and delete blog posts.
*** +15 points 

- Search: Users should be able to search for blog posts by title or content.
*** +15 points 

- Responsive Design: The web application should be responsive and work well on different screen sizes.
*** +15 points

Stretch Goals:
- User Profile: Users should have a profile page that displays their personal information and lists their blog posts.
*** +5 bonus points (above the 60 defined for the lab)

- Commenting: Users should be able to comment on blog posts.
*** +5 bonus points
```

**Key Points:**
- Base requirements total 60 points (max_score in config)
- Bonus points explicitly noted as "above the 60 defined"
- Point values marked with `*** +XX points`

---

### Configuration File
**File:** `docs/examples/grading_config_example.json`

```json
{
  "title": "docs/examples/grading_config_example.json",
  "assignment_pattern": "student_*",
  "grading_key_file": "grading_key_example.txt",
  "required_files": [
    "**/models.py",
    "**/admin.py",
    "**/settings.py",
    "**/views.py",
    "**/urls.py(2)",
    "**/*.css"
  ],
  "max_score": 60,
  "language_profile": ["python", "web"],
  "exclusions": []
}
```

**Configuration Breakdown:**

| Field | Purpose | Example Value |
|-------|---------|---------------|
| `assignment_pattern` | Glob pattern matching student folders | `student_*` matches `student_1`, `student_2` |
| `grading_key_file` | Path to grading rubric | `grading_key_example.txt` |
| `required_files` | Files that must exist | `**/models.py` finds models.py anywhere |
| `max_score` | Base points (before bonus) | `60` |
| `language_profile` | Tech stack hints for AI | `["python", "web"]` |
| `exclusions` | Patterns to ignore | `[]` (none in this example) |

**Special Pattern:** `**/urls.py(2)` means "exactly 2 urls.py files must exist"

---

### Student Submissions

**student_1:** Basic implementation
- Has all required files
- Implements all 4 base requirements
- No stretch goals implemented

**student_2:** Enhanced implementation  
- Has all required files
- Implements all 4 base requirements
- Implements 1.5 stretch goals (commenting complete, profile partial)
- Should receive bonus points

---

## Step 2: Set Up Environment

### Create Configuration Directory

From the example directory:

```bash
cd docs/examples/grading_assignment_example
```

### Verify File Structure

```
grading_assignment_example/
├── student_1/
│   └── myproject/
│       ├── manage.py
│       ├── socialproj/
│       │   ├── settings.py
│       │   ├── urls.py
│       │   └── ...
│       └── socialprojapp/
│           ├── models.py
│           ├── admin.py
│           ├── views.py
│           ├── urls.py
│           └── ...
└── student_2/
    └── myblogproject/
        ├── manage.py
        ├── myblogproject/
        │   ├── settings.py
        │   ├── urls.py
        │   └── ...
        ├── accounts/
        │   ├── models.py
        │   ├── views.py
        │   └── ...
        └── blog/
            ├── models.py
            ├── admin.py
            ├── views.py
            ├── urls.py
            └── ...
```

### Check API Key Setup

Ensure your `.env` file at the repository root contains:

```bash
OPENAI_API_KEY=sk-proj-...your-actual-key...
```

---

## Step 3: Run the Grading Command

From the `grading_assignment_example` directory:

```bash
repo-grading-assistant ../../grading_config_example.json
```

**Note:** Path is relative to current directory pointing to the config file.

---

## Step 4: Watch the Process

You'll see output similar to:

```
🎓 Repository Grading Assistant v1.0.7
═══════════════════════════════════════════════════════════

Configuration loaded: docs/examples/grading_config_example.json
Assignment pattern: student_*
Required files: **/models.py, **/admin.py, **/settings.py, **/views.py, **/urls.py(2), **/*.css
Max score: 60
Language profile: python, web

Scanning for student repositories matching pattern: student_*
Found 2 student repositories

Processing: student_1
  ✓ Required files found: 6/6
  ⚙ Calling OpenAI API with gpt-5-mini...
  ✓ Grade: 60/60 (No bonus)
  
Processing: student_2  
  ✓ Required files found: 6/6
  ⚙ Calling OpenAI API with gpt-5-mini...
  ✓ Grade: 68/60 (+8 bonus points)

Grading complete! Results saved to grade_summary.txt and grade_summary.csv
```

---

## Step 5: Review the Output Files

### grade_summary.txt

Each student gets a detailed evaluation:

```text
================================================================================
Student: student_2
Grade: 68 out of 60 (Max: 60, Bonus: +8)
Evaluation Date: 2026-01-28T15:30:45
================================================================================

REQUIREMENTS ANALYSIS
─────────────────────────────────────────────────────────────────────────────

✓ Authentication (15/15 points)
  - Implemented Django authentication system
  - User registration, login, and logout working
  - Code found in: accounts/views.py, accounts/forms.py

✓ CRUD Operations (15/15 points)
  - Full CRUD implementation for blog posts
  - CreateView, UpdateView, DeleteView properly configured
  - Code found in: blog/views.py, blog/urls.py

✓ Search Functionality (15/15 points)
  - Search implemented using Django Q objects
  - Searches title and content fields
  - Code found in: blog/views.py (SearchView)

✓ Responsive Design (15/15 points)
  - Bootstrap framework integrated
  - Mobile-responsive templates confirmed
  - Code found in: blog/templates/base.html

STRETCH GOALS (BONUS)
─────────────────────────────────────────────────────────────────────────────

✓ Commenting System (+5 bonus points)
  - Comment model with ForeignKey to Post
  - Comment creation and display implemented
  - Code found in: blog/models.py (Comment), blog/views.py

◐ User Profile (+3 bonus points - partial implementation)
  - Profile page displays user information
  - Lists user's posts
  - Missing: Edit profile functionality
  - Code found in: accounts/views.py (ProfileView)

MISSING FILES
─────────────────────────────────────────────────────────────────────────────
None - all required files present

ADDITIONAL OBSERVATIONS
─────────────────────────────────────────────────────────────────────────────
- Clean code structure with separate apps (accounts, blog)
- Good use of Django best practices
- Well-organized templates
- Could improve: Add tests, enhance error handling

FINAL GRADE: 68/60
(Base: 60, Bonus: +8)
```

### grade_summary.csv

Spreadsheet-compatible output for record keeping:

```csv
student_folder,grade,max_score,bonus_points,timestamp,missing_required_files,evaluation_notes
student_1,60,60,0,2026-01-28T15:30:30,"","All requirements met. Clean implementation."
student_2,68,60,8,2026-01-28T15:30:45,"","Excellent work with bonus features. Commenting fully implemented, profile partially completed."
```

**Usage:** Import into Excel/Google Sheets for gradebook integration.

---

## Step 6: Understanding the Evaluation

### How Points Are Calculated

1. **Base Score (0-60):** AI evaluates each requirement against the grading key
2. **Bonus Points:** Awarded for stretch goals beyond the 60-point maximum
3. **Partial Credit:** AI can award partial points (e.g., 3/5 for incomplete stretch goal)
4. **File Validation:** Missing required files noted but grading still proceeds

### Required File Cardinality

The pattern `**/urls.py(2)` ensures exactly 2 `urls.py` files exist:
- Project-level: `myblogproject/urls.py`
- App-level: `blog/urls.py`

**If cardinality fails:**
```
⚠ Warning: Expected 2 urls.py files but found 1
  Found: myblogproject/urls.py
  This may indicate missing URL configuration
```

Grading continues but warning is included in the report.

---

## Customizing for Your Assignment

### 1. Create Your Grading Key

Create a text file listing requirements with point markers:

```text
# My Assignment - Python Calculator

Core Requirements:
- Addition function with proper error handling
*** +10 points

- Subtraction function with proper error handling  
*** +10 points

- Multiplication function with proper error handling
*** +10 points

- Division function with zero-division handling
*** +10 points

Bonus Features:
- Square root operation
*** +5 bonus points

- Exponentiation operation
*** +5 bonus points
```

**Point Marker Format:** `*** +XX points` or `*** +XX bonus points`

### 2. Create Your Configuration

```json
{
  "title": "Python Calculator Assignment",
  "assignment_pattern": "student_*",
  "grading_key_file": "calculator_grading_key.txt",
  "required_files": [
    "calculator.py",
    "test_calculator.py",
    "README.md"
  ],
  "max_score": 40,
  "language_profile": ["python"],
  "exclusions": ["__pycache__", "*.pyc", ".venv"]
}
```

### 3. Organize Student Submissions

```
my_assignment/
├── grading_config.json
├── grading_key.txt
├── student_alice/
│   ├── calculator.py
│   ├── test_calculator.py
│   └── README.md
├── student_bob/
│   ├── calculator.py
│   ├── test_calculator.py
│   └── README.md
└── student_charlie/
    ├── calculator.py
    └── README.md  # Missing test file!
```

### 4. Run Grading

```bash
cd my_assignment
repo-grading-assistant grading_config.json
```

---

## Tips for Effective Grading

### 1. Test Configuration First

Run with a single student to verify configuration:

```json
"assignment_pattern": "student_alice"
```

### 2. Adjust Max Score Carefully

The `max_score` should equal the sum of base requirement points (not including bonuses):

```text
Base requirements: 10 + 10 + 10 + 10 = 40  ← max_score = 40
Bonus features: 5 + 5 = 10                 ← not counted in max_score
```

### 3. Use Precise File Patterns

| Pattern | Matches | Use Case |
|---------|---------|----------|
| `calculator.py` | Root level only | Single main file |
| `**/calculator.py` | Any directory level | Flexible structure |
| `src/calculator.py` | Exact path | Required structure |
| `*.py` | Root level Python files | Any Python file |
| `**/*.py` | All Python files recursively | Python project |
| `**/test_*.py(3)` | Exactly 3 test files | Specific count |

### 4. Review AI Evaluations

The AI is powerful but may occasionally:
- Miss edge cases in complex code
- Over/under award partial credit
- Not catch logic errors that pass syntax checks

**Recommendation:** Spot-check 10-20% of grades, especially borderline cases.

### 5. Iterate on Grading Keys

After reviewing results, you may refine your grading key:

**Before:**
```text
- Authentication system
*** +15 points
```

**After (more specific):**
```text
- Authentication system with the following:
  * User registration with email validation
  * Login/logout functionality  
  * Password reset capability
  * Session management
*** +15 points (partial credit for incomplete implementations)
```

More specific keys yield more consistent AI evaluations.

---

## Troubleshooting

### Issue: "No student repositories found"

**Cause:** Pattern doesn't match folders

**Solution:** Check pattern matches folder names exactly:
```bash
ls  # See actual folder names
```

If folders are named `submission_1`, `submission_2`:
```json
"assignment_pattern": "submission_*"
```

### Issue: "Required file not found: calculator.py"

**Cause:** Student structure differs from expected

**Options:**
1. Ask students to fix structure
2. Adjust pattern to be more flexible: `**/calculator.py`
3. Remove from required_files if not critical

### Issue: Grades seem too high/low

**Cause:** Grading key may be ambiguous

**Solution:** Review and refine grading key with more specific criteria. Compare AI evaluation against actual code for a few students.

### Issue: API costs higher than expected

**Cause:** Large code files or many students

**Solution:**
- Use `exclusions` to skip node_modules, build files, etc.
- Check [OpenAI pricing](https://openai.com/api/pricing/) for current rates
- Consider gpt-5-mini for lower costs (already the default)

---

## Next Steps

1. **Try the example:** Run grading on the included example data
2. **Customize:** Create your own grading key and configuration  
3. **Test:** Grade a single student submission first
4. **Scale:** Process your entire class once confident
5. **Iterate:** Refine grading keys based on results

For more information, see:
- [README.md](../README.md) - Full documentation
- [QUICKSTART.md](../QUICKSTART.md) - Setup instructions
- [FAQ](../README.md#faq) - Common questions

---

**Questions or issues?** Open an issue on GitHub or see [CONTRIBUTING.md](../CONTRIBUTING.md) for support options.
