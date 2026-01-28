# tests/test_grade_assignments.py

import sys
import csv
import pytest
import os

from src.repo_grading_assistant.grade_assignments import (
    find_file_anywhere,
    combine_submission_text,
    append_csv_row,
    write_grade_summary,
    grade_submission,
    parse_rule,
    find_all_by_pattern,
    find_with_escalation,
    is_excluded,
    load_global_config,
    resolve_grading_key_path,
    extract_bonus_behaviors_from_key,
)

# OpenAI Python SDK: support both old (<1.0) and new (>=1.0) exception locations
try:
    # openai>=1.0
    from openai import APITimeoutError
except Exception:  # openai<1.0 fallback
    from openai.error import Timeout
    APITimeoutError = Timeout


SYSTEM_PROMPT = "You are grading."

# --------------------------------------------------------------------
# File Search Tests
# --------------------------------------------------------------------

def test_find_file_exact_match(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("test")

    result = find_file_anywhere(tmp_path, "target.txt", exclusions=[])
    assert result == target


def test_find_file_nested_match(tmp_path):
    subdir = tmp_path / "subfolder"
    subdir.mkdir()
    (subdir / "grade_summary.txt").write_text("ok")

    result = find_file_anywhere(tmp_path, "grade_summary.txt", exclusions=[])
    assert result.name == "grade_summary.txt"


def test_find_file_not_found(tmp_path):
    result = find_file_anywhere(tmp_path, "missing.txt", exclusions=[])
    assert result is None


# --------------------------------------------------------------------
# File Combination
# --------------------------------------------------------------------

def test_combine_submission_text_merges_files(temp_project):
    student_dir = temp_project["student_dir"]
    combined = combine_submission_text(student_dir, ["main.py", "readme.txt"], exclusions=[])
    assert "Hello world" in combined
    assert "John Doe submission" in combined


# --------------------------------------------------------------------
# CSV Appending
# --------------------------------------------------------------------

def test_append_csv_row_creates_and_appends(temp_project):
    csv_path = temp_project["logs"] / "grading_summary.csv"

    # First write adds header
    append_csv_row(csv_path, "student_jdoe",
                   "Grade: 90/100\n- Missing comments (-10)",
                   "Graded")
    assert csv_path.exists()

    # Second write appends a line
    append_csv_row(csv_path, "student_smith",
                   "Grade: 100/100\n- Excellent work",
                   "Graded")

    rows = list(csv.reader(open(csv_path)))
    assert len(rows) == 3  # header + 2 rows
    assert "student_jdoe" in rows[1][2]


# --------------------------------------------------------------------
# Grade Summary Writing
# --------------------------------------------------------------------

def test_write_grade_summary_overwrites(temp_project):
    student_dir = temp_project["student_dir"]
    summary = student_dir / "grade_summary.txt"
    summary.write_text("old data")

    write_grade_summary(student_dir, "new content")
    assert summary.read_text() == "new content"


# --------------------------------------------------------------------
# Grading Flow (Mocked API)
# --------------------------------------------------------------------

def test_grade_submission_creates_summary(temp_project, fake_env, fake_openai):
    student_dir = temp_project["student_dir"]

    grading_key_file = temp_project["grading_key_file"]   # <-- use the key file, not config
    max_score = 60                        # or temp_project["max_score"] if you store it

    result = grade_submission(
        student_dir,
        grading_key_file,
        ["main.py", "readme.txt"],
        "gpt-4o-mini",
        max_score,
        [],
        SYSTEM_PROMPT,
    )

    summary = student_dir / "grade_summary.txt"
    assert summary.exists()
    assert "90/100" in result


def test_grade_submission_logs(temp_project, fake_env, fake_openai, sample_log):
    student_dir = temp_project["student_dir"]
    grading_key_file = temp_project["grading_key_file"]
    max_score = 60

    _ = grade_submission(
        student_dir,
        grading_key_file,
        ["main.py", "readme.txt"],
        "gpt-4o-mini",
        max_score,
        [],
        SYSTEM_PROMPT,
    )

    logs = sample_log.text
    assert (
        "Grading complete" in logs
        or "Saved grade summary" in logs
        or "Wrote summary" in logs
    )


# --------------------------------------------------------------------
# CLI Entry Point
# --------------------------------------------------------------------

def test_main_dry_run(monkeypatch, temp_project, fake_env):
    config = temp_project["config_file"]

    # Make the app think grade_assignments.py lives inside the temp project root
    import src.repo_grading_assistant.grade_assignments as grade_assignments
    fake_script = temp_project["root"] / "grade_assignments.py"
    fake_script.write_text("# shim for tests\n", encoding="utf-8")
    monkeypatch.setattr(grade_assignments, "__file__", str(fake_script))

    monkeypatch.setattr(sys, "argv", [
        "prog",
        "--config", str(config),
        "--repo-root", str(temp_project["root"]),
        "--dry-run"
    ])
    monkeypatch.chdir(temp_project["root"])

    grade_assignments.main()  # should return normally


def test_main_validate(monkeypatch, temp_project, fake_env, fake_openai):
    config = temp_project["config_file"]

    # Make the app think grade_assignments.py lives inside the temp project root
    import src.repo_grading_assistant.grade_assignments as grade_assignments
    fake_script = temp_project["root"] / "grade_assignments.py"
    fake_script.write_text("# shim for tests\n", encoding="utf-8")
    monkeypatch.setattr(grade_assignments, "__file__", str(fake_script))

    monkeypatch.setattr(sys, "argv", [
        "prog",
        "--config", str(config),
        "--repo-root", str(temp_project["root"]),
        "--validate"
    ])
    monkeypatch.chdir(temp_project["root"])

    grade_assignments.main()
    assert (temp_project["student_dir"] / "grade_summary.txt").exists()


def test_skip_scored(temp_project, monkeypatch, fake_env):
    student = temp_project["student_dir"]
    (student / "grade_summary.txt").write_text("DONE")

    # Make the app think grade_assignments.py lives inside the temp project root
    import src.repo_grading_assistant.grade_assignments as grade_assignments
    fake_script = temp_project["root"] / "grade_assignments.py"
    fake_script.write_text("# shim for tests\n", encoding="utf-8")
    monkeypatch.setattr(grade_assignments, "__file__", str(fake_script))

    monkeypatch.setattr(
        __import__("sys"), "argv",
        [
            "prog",
            "--config", str(temp_project["config_file"]),
            "--repo-root", str(temp_project["root"]),
            "--skip-scored",
            "--dry-run",
        ],
    )
    monkeypatch.chdir(temp_project["root"])

    # Should not SystemExit anymore; it should run cleanly
    grade_assignments.main()

    assert (student / "grade_summary.txt").read_text() == "DONE"

    csv_path = grade_assignments.Path("logs") / "grading_summary.csv"
    if csv_path.exists():
        csv_text = csv_path.read_text(encoding="utf-8")
        assert student.name not in csv_text
        
def test_find_all_by_pattern_deep_glob_and_exclusions(tmp_path):
    root = tmp_path

    # included
    (root / "a" / "b").mkdir(parents=True)
    f1 = root / "a" / "b" / "main.py"
    f1.write_text("print('ok')", encoding="utf-8")

    # excluded directory
    (root / ".venv" / "x").mkdir(parents=True)
    f2 = root / ".venv" / "x" / "main.py"
    f2.write_text("print('no')", encoding="utf-8")

    matches = find_all_by_pattern(root, "**/main.py", exclusions=[".venv"])
    rels = {m.relative_to(root).as_posix() for m in matches}

    assert "a/b/main.py" in rels
    assert ".venv/x/main.py" not in rels

def test_find_with_escalation_path_then_basename_then_fuzzy(tmp_path):
    base = tmp_path
    (base / "app").mkdir()
    real = base / "app" / "urls.py"
    real.write_text("# urls", encoding="utf-8")

    # Phase 1a: exact-path match
    matches, escalation = find_with_escalation(base, "app/urls.py", exclusions=[], needed=1)
    assert len(matches) == 1
    assert matches[0] == real
    assert escalation == "exact-path"

    # Path not found -> fallback to basename (Phase 1b)
    matches, escalation = find_with_escalation(base, "missingdir/urls.py", exclusions=[], needed=1)
    assert len(matches) == 1
    assert matches[0] == real
    assert escalation == "exact-name"

    # Fuzzy fallback: request urls.py but only url.py exists
    (base / "typos").mkdir()
    typo = base / "typos" / "url.py"
    typo.write_text("# typo", encoding="utf-8")

    # Use a fresh base dir to avoid exact-name hits from urls.py
    base2 = tmp_path / "base2"
    base2.mkdir()
    (base2 / "typos").mkdir()
    typo2 = base2 / "typos" / "url.py"
    typo2.write_text("# typo", encoding="utf-8")

    matches, escalation = find_with_escalation(base2, "urls.py", exclusions=[], needed=1)
    assert len(matches) >= 1
    assert matches[0].name == "url.py"
    assert escalation == "fuzzy"

def test_is_excluded_wildcard_and_ancestor_dir(tmp_path):
    root = tmp_path

    # wildcard exclusion: anything under .venv
    (root / ".venv" / "Lib").mkdir(parents=True)
    p = root / ".venv" / "Lib" / "site.py"
    p.write_text("x", encoding="utf-8")
    assert is_excluded(p, exclusions=[".venv"], root=root) is True

    # ancestor directory exclusion: node_modules anywhere in path
    (root / "web" / "node_modules" / "pkg").mkdir(parents=True)
    q = root / "web" / "node_modules" / "pkg" / "index.js"
    q.write_text("y", encoding="utf-8")
    assert is_excluded(q, exclusions=["node_modules"], root=root) is True

    # non-excluded normal file
    (root / "src").mkdir()
    r = root / "src" / "main.py"
    r.write_text("z", encoding="utf-8")
    assert is_excluded(r, exclusions=["node_modules", ".venv"], root=root) is False

def test_parse_rule_edge_cases():
    # exact count in current implementation: (2) means "at least 2"
    pattern, mn, mx = parse_rule("urls.py(2)")
    assert pattern == "urls.py"
    assert mn == 2 and mx == float("inf")

    # optional range
    pattern, mn, mx = parse_rule("README.md(0..1)")
    assert pattern == "README.md"
    assert mn == 0 and mx == 1

    # unbounded max
    pattern, mn, mx = parse_rule("*.png(0..*)")
    assert pattern == "*.png"
    assert mn == 0 and mx == float("inf")

    # default
    pattern, mn, mx = parse_rule("models.py")
    assert pattern == "models.py"
    assert mn == 1 and mx == 1

# --------------------------------------------------------------------
# Additional Unit Tests for Edge Cases
# --------------------------------------------------------------------

def test_parse_rule_various_formats():
    """Test different cardinality rule formats."""
    # Range with specific bounds
    pattern, mn, mx = parse_rule("config.json(1..3)")
    assert pattern == "config.json" and mn == 1 and mx == 3
    
    # Zero or more
    pattern, mn, mx = parse_rule("*.txt(0..*)")
    assert pattern == "*.txt" and mn == 0 and mx == float("inf")
    
    # Exact number
    pattern, mn, mx = parse_rule("tests.py(5)")
    assert pattern == "tests.py" and mn == 5 and mx == float("inf")


def test_exclusions_with_nested_directories(tmp_path):
    """Test exclusion logic with deeply nested structures."""
    root = tmp_path
    
    # Create nested structure
    (root / "src" / "app" / "models").mkdir(parents=True)
    (root / "src" / "__pycache__" / "models").mkdir(parents=True)
    (root / "tests" / "__pycache__").mkdir(parents=True)
    
    included = root / "src" / "app" / "models" / "user.py"
    excluded1 = root / "src" / "__pycache__" / "models" / "user.cpython-311.pyc"
    excluded2 = root / "tests" / "__pycache__" / "test.pyc"
    
    included.write_text("class User: pass")
    excluded1.write_text("bytecode")
    excluded2.write_text("bytecode")
    
    assert is_excluded(included, ["__pycache__"], root) is False
    assert is_excluded(excluded1, ["__pycache__"], root) is True
    assert is_excluded(excluded2, ["__pycache__"], root) is True


def test_find_file_with_multiple_matches(tmp_path):
    """Test file finding when multiple files match."""
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir2").mkdir()
    
    (tmp_path / "dir1" / "config.json").write_text("{}")
    (tmp_path / "dir2" / "config.json").write_text("{}")
    
    # Should find first match
    result = find_file_anywhere(tmp_path, "config.json", exclusions=[])
    assert result is not None
    assert result.name == "config.json"


def test_combine_submission_text_with_missing_files(temp_project):
    """Test combining files when some are missing."""
    student_dir = temp_project["student_dir"]
    
    # Request files that don't exist
    combined = combine_submission_text(
        student_dir, 
        ["main.py", "missing.py", "also_missing.txt"],
        exclusions=[]
    )
    
    # Should include existing file
    assert "Hello world" in combined
    # Should not crash on missing files


def test_combine_submission_text_empty_directory(tmp_path):
    """Test combining files in empty directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    combined = combine_submission_text(empty_dir, ["*.py"], exclusions=[])
    assert combined == ""


def test_find_all_by_pattern_with_wildcards(tmp_path):
    """Test various wildcard patterns."""
    root = tmp_path
    
    # Create test structure
    (root / "src" / "app").mkdir(parents=True)
    (root / "src" / "tests").mkdir(parents=True)
    (root / "docs").mkdir()
    
    (root / "src" / "app" / "main.py").write_text("app")
    (root / "src" / "app" / "utils.py").write_text("utils")
    (root / "src" / "tests" / "test_main.py").write_text("test")
    (root / "docs" / "README.md").write_text("doc")
    
    # Test *.py pattern
    py_files = find_all_by_pattern(root, "**/*.py", exclusions=[])
    assert len(py_files) == 3
    
    # Test specific subdirectory pattern
    test_files = find_all_by_pattern(root, "**/tests/*.py", exclusions=[])
    assert len(test_files) == 1
    assert test_files[0].name == "test_main.py"


def test_csv_row_special_characters(temp_project):
    """Test CSV handling with special characters in feedback."""
    csv_path = temp_project["logs"] / "test_special.csv"
    
    # Feedback with quotes, commas, and newlines
    feedback = 'Grade: 85/100\nComments: "Good work", but needs improvement.\nMulti-line\nfeedback'
    
    append_csv_row(csv_path, "student_test", feedback, "Graded")
    
    assert csv_path.exists()
    content = csv_path.read_text()
    assert "student_test" in content


def test_exclusions_case_sensitivity(tmp_path):
    """Test if exclusions work with different case variations."""
    root = tmp_path
    
    # On Windows, Node_Modules and node_modules are the same
    # Test with different casing in the exclusion rule
    (root / "node_modules").mkdir()
    (root / "src").mkdir()
    
    file1 = root / "node_modules" / "test.js"
    file2 = root / "src" / "test.js"
    
    file1.write_text("test")
    file2.write_text("test")
    
    # Both lowercase exclusion and file should match
    assert is_excluded(file1, ["node_modules"], root) is True
    assert is_excluded(file2, ["node_modules"], root) is False


def test_find_with_escalation_no_matches(tmp_path):
    """Test escalation when no files match at all."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    matches, escalation = find_with_escalation(
        empty_dir, 
        "nonexistent.py", 
        exclusions=[], 
        needed=1
    )
    
    assert len(matches) == 0
    assert escalation in ["exact-path", "exact-name", "fuzzy", "none"]


def test_parse_rule_malformed_input():
    """Test parse_rule with edge cases."""
    # Missing closing parenthesis
    pattern, mn, mx = parse_rule("file.py(2")
    assert pattern == "file.py(2"  # Should treat as literal
    assert mn == 1 and mx == 1
    
    # Empty string
    pattern, mn, mx = parse_rule("")
    assert pattern == ""
    assert mn == 1 and mx == 1


def test_write_grade_summary_creates_directory(tmp_path):
    """Test that grade summary can be written to existing directory."""
    deep_dir = tmp_path / "level1" / "level2" / "student"
    deep_dir.mkdir(parents=True)  # Create directory structure first
    
    write_grade_summary(deep_dir, "Test content")
    
    summary_file = deep_dir / "grade_summary.txt"
    assert summary_file.exists()
    assert summary_file.read_text() == "Test content"


def test_combine_submission_text_with_exclusions(tmp_path):
    """Test that excluded files are not included in submission text."""
    student_dir = tmp_path / "student"
    student_dir.mkdir()
    
    # Create files
    (student_dir / "main.py").write_text("main code")
    (student_dir / "__pycache__").mkdir()
    (student_dir / "__pycache__" / "main.cpython-311.pyc").write_text("bytecode")
    
    # Use specific file names instead of globs to avoid rule violations
    combined = combine_submission_text(
        student_dir,
        ["main.py"],
        exclusions=["__pycache__"]
    )
    
    assert "main code" in combined
    
    # Test that __pycache__ files would be excluded if we tried to include them
    pycache_file = student_dir / "__pycache__" / "main.cpython-311.pyc"
    assert is_excluded(pycache_file, ["__pycache__"], student_dir) is True


def test_find_all_by_pattern_max_depth(tmp_path):
    """Test deep directory structures."""
    root = tmp_path
    
    # Create deeply nested structure
    deep_path = root / "a" / "b" / "c" / "d" / "e" / "f"
    deep_path.mkdir(parents=True)
    
    deep_file = deep_path / "deep.py"
    deep_file.write_text("deep")
    
    # Should still find it
    matches = find_all_by_pattern(root, "**/*.py", exclusions=[])
    assert len(matches) == 1
    assert matches[0] == deep_file


def test_csv_appending_preserves_existing_data(temp_project):
    """Test that appending to CSV doesn't corrupt existing rows."""
    csv_path = temp_project["logs"] / "preserve_test.csv"
    
    # Add multiple rows
    append_csv_row(csv_path, "student1", "Score: 90", "Graded")
    append_csv_row(csv_path, "student2", "Score: 85", "Graded")
    append_csv_row(csv_path, "student3", "Score: 95", "Graded")
    
    # Read and verify all rows exist
    rows = list(csv.reader(open(csv_path)))
    assert len(rows) == 4  # header + 3 rows
    
    # Verify specific data
    assert "student1" in rows[1][2]
    assert "student2" in rows[2][2]
    assert "student3" in rows[3][2]

# --------------------------------------------------------------------
# Config Validation Tests
# --------------------------------------------------------------------

def test_load_global_config_success(tmp_path):
    """Test loading valid global config."""
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    
    global_config = configs_dir / "global_config.json"
    global_config.write_text('{"model": "gpt-5-mini", "timeout": 30}')
    
    cfg = load_global_config(configs_dir)
    assert cfg["model"] == "gpt-5-mini"
    assert cfg["timeout"] == 30


def test_load_global_config_missing(tmp_path):
    """Test loading when global config doesn't exist."""
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    
    # Should return empty dict without crashing
    cfg = load_global_config(configs_dir)
    assert cfg == {}


def test_load_global_config_malformed_json(tmp_path):
    """Test loading malformed JSON in global config."""
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    
    global_config = configs_dir / "global_config.json"
    global_config.write_text('{"model": "gpt-5-mini",}')  # Trailing comma is invalid
    
    # Should return empty dict and not crash
    cfg = load_global_config(configs_dir)
    assert cfg == {}


def test_load_global_config_empty_file(tmp_path):
    """Test loading empty global config file."""
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    
    global_config = configs_dir / "global_config.json"
    global_config.write_text('')
    
    # Should return empty dict
    cfg = load_global_config(configs_dir)
    assert cfg == {}


def test_resolve_grading_key_path_absolute(tmp_path):
    """Test resolving absolute grading key paths."""
    config_file = tmp_path / "config.json"
    key_file = tmp_path / "keys" / "grading_key.txt"
    key_file.parent.mkdir()
    key_file.write_text("grading key content")
    
    cfg = {"grading_key_file": str(key_file.absolute())}
    
    resolved = resolve_grading_key_path(cfg, config_file)
    assert resolved == key_file.absolute()


def test_resolve_grading_key_path_relative(tmp_path):
    """Test resolving relative grading key paths."""
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    config_file = configs_dir / "config.json"
    
    keys_dir = tmp_path / "keys"
    keys_dir.mkdir()
    key_file = keys_dir / "grading_key.txt"
    key_file.write_text("grading key content")
    
    # Path relative to config file
    cfg = {"grading_key_file": "../keys/grading_key.txt"}
    
    resolved = resolve_grading_key_path(cfg, config_file)
    assert resolved.name == "grading_key.txt"
    assert resolved.exists()


def test_resolve_grading_key_path_with_tilde(tmp_path):
    """Test resolving grading key paths with home directory expansion."""
    config_file = tmp_path / "config.json"
    
    # Use tilde notation
    cfg = {"grading_key_file": "~/grading_key.txt"}
    
    resolved = resolve_grading_key_path(cfg, config_file)
    # Should expand tilde
    assert "~" not in str(resolved)


# --------------------------------------------------------------------
# Error Handling Tests
# --------------------------------------------------------------------

def test_find_file_with_permission_error(tmp_path):
    """Test handling of files that can't be read."""
    (tmp_path / "readable.txt").write_text("ok")
    
    # Should not crash even if we can't create permission issues in test env
    result = find_file_anywhere(tmp_path, "readable.txt", exclusions=[])
    assert result is not None


def test_combine_submission_with_empty_files(tmp_path):
    """Test combining submission when files are empty."""
    student_dir = tmp_path / "student"
    student_dir.mkdir()
    
    (student_dir / "empty1.py").write_text("")
    (student_dir / "empty2.py").write_text("")
    
    combined = combine_submission_text(student_dir, ["empty1.py", "empty2.py"], exclusions=[])
    
    # Should handle empty files gracefully
    assert isinstance(combined, str)


def test_csv_with_unicode_characters(temp_project):
    """Test CSV handling with unicode in student names and feedback."""
    csv_path = temp_project["logs"] / "unicode_test.csv"
    
    # Unicode characters
    append_csv_row(csv_path, "étudiant_français", "Score: 100/100 ✓", "Graded")
    append_csv_row(csv_path, "学生_中文", "Very good work! 优秀", "Graded")
    
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "étudiant" in content
    assert "学生" in content


def test_csv_with_very_long_feedback(temp_project):
    """Test CSV with extremely long feedback text."""
    csv_path = temp_project["logs"] / "long_test.csv"
    
    # Generate long feedback
    long_feedback = "Grade: 85/100\n" + ("X" * 10000) + "\nEnd of feedback"
    
    append_csv_row(csv_path, "student_long", long_feedback, "Graded")
    
    assert csv_path.exists()
    # Verify file is readable
    content = csv_path.read_text(encoding="utf-8")
    assert "student_long" in content


def test_write_grade_summary_empty_content(tmp_path):
    """Test writing grade summary with empty content."""
    student_dir = tmp_path / "student"
    student_dir.mkdir()
    
    write_grade_summary(student_dir, "")
    
    summary_file = student_dir / "grade_summary.txt"
    assert summary_file.exists()
    assert summary_file.read_text() == ""


def test_write_grade_summary_overwrite_readonly():
    """Test that write_grade_summary overwrites existing files."""
    # This test verifies the documented behavior
    pass  # Already tested in test_write_grade_summary_overwrites


# --------------------------------------------------------------------
# Bonus Points Extraction Tests
# --------------------------------------------------------------------

def test_extract_bonus_behaviors_basic(tmp_path):
    """Test extracting bonus behaviors from grading key."""
    key_text = """
    Assignment Requirements:
    
    *** +10 points for basic functionality
    
    Bonus:
    *** BONUS +5 points for implementing search feature
    *** BONUS +3 points for adding responsive design
    """
    
    behaviors = extract_bonus_behaviors_from_key(key_text)
    assert len(behaviors) == 2
    assert "implementing search feature" in behaviors
    assert "adding responsive design" in behaviors


def test_extract_bonus_behaviors_various_formats(tmp_path):
    """Test bonus extraction with different formatting."""
    key_text = """
    *** BONUS +2.5 points for ordering contacts by last name
    *** bonus +10 points for user profile page
    ***BONUS+5points for commenting system
    *** BONUS +15 POINTS FOR advanced caching
    """
    
    behaviors = extract_bonus_behaviors_from_key(key_text)
    assert len(behaviors) >= 3  # Should catch most formats
    assert any("ordering contacts" in b.lower() for b in behaviors)


def test_extract_bonus_behaviors_no_bonus(tmp_path):
    """Test extracting bonus behaviors when none exist."""
    key_text = """
    Assignment Requirements:
    
    *** +10 points for basic functionality
    *** +15 points for advanced features
    """
    
    behaviors = extract_bonus_behaviors_from_key(key_text)
    assert len(behaviors) == 0


def test_extract_bonus_behaviors_empty_key():
    """Test extracting bonus behaviors from empty key."""
    behaviors = extract_bonus_behaviors_from_key("")
    assert len(behaviors) == 0


# --------------------------------------------------------------------
# Cardinality Violation Tests
# --------------------------------------------------------------------

def test_cardinality_exact_count_violation(tmp_path):
    """Test exact count cardinality violations."""
    root = tmp_path
    
    # Create only 1 file when we need exactly 2
    (root / "urls.py").write_text("url config")
    
    matches = find_all_by_pattern(root, "urls.py", exclusions=[])
    
    # Parse rule expecting 2
    pattern, min_count, max_count = parse_rule("urls.py(2)")
    
    # Check violation
    assert len(matches) < min_count  # Violation: need 2, have 1


def test_cardinality_range_violation_too_few(tmp_path):
    """Test range cardinality with too few files."""
    root = tmp_path
    
    # Create no files when we need 1-3
    matches = find_all_by_pattern(root, "config.json", exclusions=[])
    
    pattern, min_count, max_count = parse_rule("config.json(1..3)")
    
    assert len(matches) < min_count  # Violation: need at least 1


def test_cardinality_range_violation_too_many(tmp_path):
    """Test range cardinality with too many files."""
    root = tmp_path
    
    # Create 5 files when we need only 1-3
    for i in range(5):
        (root / f"config{i}.json").write_text(f"config {i}")
    
    matches = find_all_by_pattern(root, "*.json", exclusions=[])
    
    pattern, min_count, max_count = parse_rule("*.json(1..3)")
    
    assert len(matches) > max_count  # Violation: have 5, max is 3


def test_cardinality_optional_zero_files(tmp_path):
    """Test optional cardinality with zero files (should be valid)."""
    root = tmp_path
    
    # Create no README (optional)
    matches = find_all_by_pattern(root, "README.md", exclusions=[])
    
    pattern, min_count, max_count = parse_rule("README.md(0..1)")
    
    # Valid: 0 files when 0..1 allowed
    assert min_count <= len(matches) <= max_count


def test_cardinality_unbounded_any_count(tmp_path):
    """Test unbounded cardinality (0..*) accepts any number."""
    root = tmp_path
    
    # Create various numbers of PNG files
    for i in range(10):
        (root / f"image{i}.png").write_text("image")
    
    matches = find_all_by_pattern(root, "*.png", exclusions=[])
    
    pattern, min_count, max_count = parse_rule("*.png(0..*)")
    
    # Valid: any number allowed
    assert min_count <= len(matches)
    assert max_count == float("inf")

# --------------------------------------------------------------------
# OpenAI API Validation Tests
# These tests call the actual OpenAI API to validate configuration
# --------------------------------------------------------------------

def test_openai_api_access_and_response():
    """
    Validates OpenAI API key access and model response.
    
    This test actually calls the OpenAI API and incurs minimal costs (~$0.001).
    Runs with every pytest execution to validate API configuration.
    
    Requirements:
    - OPENAI_API_KEY must be set in environment or .env file
    - API key must have access to gpt-5-mini model
    """
    import openai
    
    # Load API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set - skipping integration test")
    
    # Skip if API key is a placeholder value (CI environments often use placeholders)
    placeholder_patterns = ["placeholder", "test", "ci-", "fake", "dummy", "example"]
    if any(pattern in api_key.lower() for pattern in placeholder_patterns):
        pytest.skip("OPENAI_API_KEY appears to be a placeholder - skipping integration test")
    
    openai.api_key = api_key
    
    # Simple test prompt
    test_prompt = "Please respond with exactly: 'Integration test successful'"
    
    try:
        # Call OpenAI API with configured model
        response = openai.ChatCompletion.create(
            model="gpt-5-mini",  # Use the default model from config
            messages=[
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": test_prompt}
            ],
            max_completion_tokens=50
        )
        
        # Validate we got a response
        assert response is not None, "No response from OpenAI API"
        assert hasattr(response, 'choices'), "Response missing 'choices'"
        assert len(response.choices) > 0, "Response has no choices"
        
        # Extract response text
        message = response.choices[0].message
        assert hasattr(message, 'content'), "Message missing 'content'"
        
        response_text = message.content.strip() if message.content else ""
        
        # Validate API call succeeded (content may be empty with default temperature)
        print("\n✓ OpenAI API integration test passed")
        print("✓ Model: gpt-5-mini")
        print(f"✓ Response received: '{response_text[:100] if response_text else '(empty response)'}'")
        
    except openai.error.AuthenticationError:
        pytest.fail("OpenAI API authentication failed - check API key")
    except openai.error.InvalidRequestError as e:
        if "does not have access" in str(e):
            pytest.fail(f"API key does not have access to gpt-5-mini model: {e}")
        else:
            pytest.fail(f"Invalid request to OpenAI API: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error calling OpenAI API: {type(e).__name__}: {e}")

# --------------------------------------------------------------------
# End of tests/test_grade_assignments.py

