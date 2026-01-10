# tests/test_grade_assignments.py

import sys
import csv
from pathlib import Path

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
)

# OpenAI Python SDK: support both old (<1.0) and new (>=1.0) exception locations
try:
    # openai>=1.0
    from openai import APIError, RateLimitError, APITimeoutError, APIConnectionError
except Exception:  # openai<1.0 fallback
    from openai.error import APIError, RateLimitError, Timeout, APIConnectionError
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
# End of tests/test_grade_assignments.py    