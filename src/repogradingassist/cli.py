# !/usr/bin/env python3
#  src/repogradingassist/cli.py
"""Command-line interface for Repo Grading Assistant."""


import argparse
from repogradingassist.grade_assignments import main as run_grader


from repogradingassist.grade_assignments import main as run_grader

def main() -> None:
    # Delegate all argument parsing to grade_assignments.py
    run_grader()

if __name__ == "__main__":
    main()
