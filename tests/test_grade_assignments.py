# tests/test_grade_assignments.py

import sys
import csv
import pytest
from src.repogradingassist.grade_assignments import (
    find_file_anywhere,
    combine_submission_text,
    append_csv_row,
    write_grade_summary,
    grade_submission,
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

    key_file = temp_project["key_file"]   # <-- use the key file, not config
    max_score = 60                        # or temp_project["max_score"] if you store it

    result = grade_submission(
        student_dir,
        key_file,
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
    key_file = temp_project["key_file"]
    max_score = 60

    _ = grade_submission(
        student_dir,
        key_file,
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
    import src.repogradingassist.grade_assignments as grade_assignments
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
    import src.repogradingassist.grade_assignments as grade_assignments
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
    import src.repogradingassist.grade_assignments as grade_assignments
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
        
# --------------------------------------------------------------------
# End of tests/test_grade_assignments.py    