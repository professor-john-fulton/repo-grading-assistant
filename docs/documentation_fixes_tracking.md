# Documentation Fixes Tracking

Last Updated: January 28, 2026

## Priority 1: Critical - Breaks Functionality or Causes Confusion

### 1.1 API Key Setup - Conflicting Instructions
**Files:** `QUICKSTART.md`, `README.md`
**Issue:** QUICKSTART.md instructs users to put API key in `.env` file, but README.md (lines 84-91) instructs using `setx` (Windows) or `export` (macOS/Linux). These are mutually exclusive approaches.
**Impact:** Users will be confused about which method to use, likely leading to setup failures.
**Fix Required:** 
- Determine which approach the code actually uses (check if python-dotenv is configured to load .env)
- Update both files to have consistent instructions
- Remove conflicting method or explain when to use each

### 1.2 Incorrect File Paths in README.md
**File:** `README.md`
**Issue:** 
- Line 171: References `prompts/base_system_prompt.txt` 
- Line 186: References `prompts/base_system_prompt.txt`
- Actual location: `src/repo_grading_assistant/data/base_system_prompt.txt`
- Line 172: References `keys/*.txt` but location unclear (should be at project root?)
**Impact:** Users following troubleshooting guide will look in wrong location
**Fix Required:** Update all path references to match actual file structure

### 1.3 Non-existent GPT Model Reference
**File:** `QUICKSTART.md` (line 2)
**Issue:** States "Setup the key to have access to the gpt-5 model" - GPT-5 doesn't exist
**Impact:** Users will be confused trying to access non-existent model
**Fix Required:** Determine correct model (likely GPT-4 or GPT-4-turbo) and update

### 1.4 Pytest Coverage Path Syntax Error
**File:** `docs/testing.md` (line 8)
**Issue:** Uses `src.repo-grading-assistant.grade_assignments` (dots with hyphens)
**Impact:** Pytest command will likely fail due to invalid module syntax
**Fix Required:** Change to proper path format (e.g., `src/repo_grading_assistant/grade_assignments`)

---

## Priority 2: Important - Significantly Affects Clarity

### 2.1 QUICKSTART.md Structural Issues
**File:** `QUICKSTART.md`
**Issue:** File contains raw notes, incomplete sentences, and mixed formatting:
- Line 1: "## Quickstart.md" (double header)
- Has unprocessed mentor suggestions at bottom
- Incomplete bullet point about creating ./keys/ directory
- Mixed instructions without clear flow
**Impact:** Confusing first experience for new users
**Fix Required:** Complete rewrite for clarity and flow

### 2.2 Typos in CONTRIBUTING.md
**File:** `CONTRIBUTING.md`
**Issue:** Multiple typos that affect professionalism:
- "stabdard" → "standard"
- "aas" → "as"
- "examing" → "examine"  
- "ythat" → "that"
- "feflected" → "reflected"
- "Camplare" → "Compare"
**Impact:** Reduces professional appearance of project
**Fix Required:** Fix all typos

### 2.3 README.md Typo
**File:** `README.md` (line 36)
**Issue:** "Likley usable" → "Likely usable"
**Impact:** Unprofessional appearance
**Fix Required:** Fix typo

### 2.4 QUICKSTART.md Typo
**File:** `QUICKSTART.md` (line 1 of content)
**Issue:** "OpeanAI" → "OpenAI"
**Impact:** Unprofessional appearance
**Fix Required:** Fix typo

### 2.5 Outdated Branch Name in CONTRIBUTING.md
**File:** `CONTRIBUTING.md`
**Issue:** References specific example branch "docs/readme-proofread" that doesn't match generic instructions
**Impact:** Confusing example in contribution workflow
**Fix Required:** Use generic branch name like "feature/my-changes" or "fix/documentation"

### 2.6 Conflicting Configuration Examples
**Files:** `configs/grading_config_example.json`, `docs/examples/grading_config_example.json`
**Issue:** Two different example files with different patterns:
- `configs/` version uses `lab-5-*` pattern and `Lab05-key.txt`
- `docs/examples/` version uses `student_*` pattern and `grading_key_example.txt`
**Impact:** Unclear which is the canonical example
**Fix Required:** 
- Consolidate to one location
- Or clearly document purpose of each
- Ensure examples match actual example data structure

---

## Priority 3: Moderate - Quality and Completeness

### 3.1 Incomplete README.md Sections
**File:** `README.md` (lines 239-244)
**Issue:** Placeholder headers without content:
- Data Privacy
- Roadmap  
- Support
- Citation
**Impact:** Appears unfinished
**Fix Required:** Either remove placeholder sections or add content

### 3.2 CHANGELOG.md Date Format
**File:** `CHANGELOG.md` (line 14)
**Issue:** Uses "1/8/26" instead of ISO format
**Impact:** Inconsistent with Keep a Changelog standard the file claims to follow
**Fix Required:** Change to "2026-01-08"

### 3.3 Sparse SECURITY.md
**File:** `SECURITY.md`
**Issue:** Very brief, missing important information:
- No mention of data handling practices (student code, API keys, logs)
- No version support policy
- No severity classification
**Impact:** Incomplete security guidance
**Fix Required:** Expand with:
- Data privacy practices
- What data to never commit
- Supported versions
- Security best practices for API keys

### 3.4 Minimal CODE_OF_CONDUCT.md
**File:** `CODE_OF_CONDUCT.md`
**Issue:** Claims to follow Contributor Covenant but severely truncated version
- Missing scope section
- Missing enforcement responsibilities
- Missing enforcement guidelines
- Missing attribution details
**Impact:** Incomplete code of conduct
**Fix Required:** Either use full Contributor Covenant 2.1 or note it's a summary with link to full version

### 3.5 Unclear Keys Directory Setup
**File:** `QUICKSTART.md`
**Issue:** Mentions creating `./keys/` directory but doesn't explain:
- Is it required or optional?
- What files go there?
- How does config reference these files?
**Impact:** Users don't know how to organize grading keys
**Fix Required:** Add clear explanation of keys directory structure and usage

---

## Priority 4: Enhancements - Nice to Have

### 4.1 Missing Architecture Documentation
**What:** No documentation explaining how the system works internally
**Why Needed:** Helps contributors understand the codebase
**Suggested Content:**
- How grading engine assembles prompts
- Flow from config → file collection → API call → output
- How cardinality rules are parsed and enforced
- Package structure explanation

### 4.2 Missing Examples Walkthrough
**What:** No detailed walkthrough of example assignment
**Why Needed:** Helps users understand expected output format
**Suggested Content:**
- Step-by-step walkthrough using example data
- Show expected `grade_summary.txt` output
- Show expected CSV row
- Explain how to create custom grading templates

### 4.3 No FAQ Section
**What:** Common questions not addressed
**Why Needed:** Reduces support burden
**Suggested Topics:**
- OpenAI API cost estimates per assignment/student
- How to handle different programming languages
- Best practices for writing grading templates
- How to handle bonus points
- What happens if student file structure differs from expected
- How to grade Jupyter notebooks vs .py files

### 4.4 Minimal Issue/PR Templates
**Files:** `docs/bug_report.md`, `docs/feature_request.md`, `docs/pull_request_template.md`
**What:** Very basic templates with minimal guidance
**Why Needed:** Better quality issues and PRs
**Suggested Improvements:**
- Add project-specific context questions
- Add examples
- Add more detailed checklists

### 4.5 Missing Installation Troubleshooting
**What:** No dedicated troubleshooting section for installation
**Why Needed:** Common setup issues not addressed
**Suggested Content:**
- Python version conflicts
- Virtual environment issues on Windows
- PATH problems
- Permission errors
- Module not found errors after installation

### 4.6 Missing Usage Examples Beyond Basics
**What:** Only basic commands shown
**Why Needed:** Users need real-world workflow examples
**Suggested Content:**
- Workflow for grading multiple assignments
- How to re-grade after template changes
- How to grade partial submissions
- How to handle late submissions
- Batch processing strategies

### 4.7 No OpenAI API Configuration Guidance
**What:** Assumes users know OpenAI API setup
**Why Needed:** First-time API users need guidance
**Suggested Content:**
- How to create OpenAI account
- Where to find API keys
- How to set spending limits
- Which models to use and why
- Token usage and cost estimation

### 4.8 Missing Contributing Guidelines for Documentation
**File:** `CONTRIBUTING.md`
**What:** Only covers code contributions
**Why Needed:** Documentation contributions are also valuable
**Suggested Content:**
- Style guide for documentation
- How to test documentation changes
- Documentation review process

### 4.9 No Integration Tests for OpenAI API
**What:** All tests are mocked; no actual API calls tested
**Why Needed:** Validate real API integration works end-to-end
**Suggested Implementation:**
- Create optional integration tests marked with `@pytest.mark.integration`
- Test actual OpenAI API key access
- Validate model name is accessible
- Test full grading flow with real API
- Only run when explicitly requested: `pytest -m integration`
- Document in testing.md
- Keep integration tests separate to avoid API costs in regular CI runs

---

## Implementation Notes

### Verification Required
Before fixing, verify:
1. Does the code actually load from `.env` file or use environment variables?
2. What OpenAI model is actually configured in the code?
3. Where should grading key files actually be stored?
4. Is there a `prompts/` directory that should exist?

### Files to Create/Check
- Verify if `.env.example` should exist
- Check if `keys/` directory needs a README
- Verify actual OpenAI model usage in code

### Testing After Fixes
- Follow installation instructions on clean system
- Run all commands in documentation
- Verify all file paths exist
- Test with example data

---

## Summary Statistics

- **Priority 1 (Critical):** 4 issues ✅ **COMPLETED**
- **Priority 2 (Important):** 6 issues
- **Priority 3 (Moderate):** 5 issues
- **Priority 4 (Enhancements):** 9 items (was 8, added integration tests)
- **Total Issues:** 24 items

**Estimated Effort:**
- Priority 1: 2-3 hours (requires code verification)
- Priority 2: 1-2 hours
- Priority 3: 2-3 hours
- Priority 4: 8-10 hours (if all implemented)

**Recommended Approach:**
1. Start with Priority 1 items (especially 1.1 - requires code inspection)
2. Fix Priority 2 typos and clarity issues (quick wins)
3. Address Priority 3 completeness issues
4. Consider Priority 4 enhancements based on user feedback
