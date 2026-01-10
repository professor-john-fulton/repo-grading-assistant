# !/usr/bin/env python3
#  src/repo-grading-assistant/cli.py
"""Command-line interface for Repo Grading Assistant."""

from repo_grading_assistant.grade_assignments import main as run_grader

def main() -> None:
    # Delegate all argument parsing to grade_assignments.py
    run_grader()

if __name__ == "__main__":
    main()
