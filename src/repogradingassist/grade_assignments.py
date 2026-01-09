#!/usr/bin/env python3

# grade_assignments.py
"""
Student Repo Grading Assistant

Automates grading of student repositories using an instructor-supplied
grading key and OpenAI’s API.

See docs/architecture.md for design details.
See README.md for usage.
"""


import argparse
import logging
import os
import sys
import time
import threading
import csv
import json
from pathlib import Path
import fnmatch
import re
import openai

# OpenAI Python SDK: support both old (<1.0) and new (>=1.0) exception locations
try:
    # openai>=1.0
    from openai import APIError, RateLimitError, APITimeoutError, APIConnectionError
except Exception:  # openai<1.0 fallback
    from openai.error import APIError, RateLimitError, Timeout, APIConnectionError
    APITimeoutError = Timeout

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass

__version__ = "0.0.6"


# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------

def setup_logging() -> None:
    """Configure both file and console logging, placing logs in ./logs/."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "grading.log"

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger("").addHandler(console)
    logging.info(f"Student Repo Grading Assistant v{__version__}")
    logging.info(f"Logging initialized → {log_file}")


# ---------------------------------------------------------------------------
# Configuration Loader
# ---------------------------------------------------------------------------

def load_config(config_path: str) -> dict:
    """Load assignment configuration from JSON file."""
    path = Path(config_path)
    if not path.exists():
        logging.error(f"Config file not found: {config_path}")
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logging.error(f"Failed to parse config JSON: {e}")
        sys.exit(1)

def load_global_config() -> dict:
    """
    Load optional global configuration (e.g., default model) from
    configs/global_config.json, located next to this script.

    This must NEVER cause the program to exit; it only provides defaults.
    """
    project_root = Path(__file__).resolve().parent
    path = project_root / "configs" / "global_config.json"

    if not path.exists():
        logging.info(f"No global config found at {path}; using built-in defaults.")
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logging.error(f"Failed to parse global config JSON ({path}): {e}")
        logging.error("Falling back to built-in defaults.")
        return {}


# ---------------------------------------------------------------------------
# Idle Marker Thread
# ---------------------------------------------------------------------------

def idle_marker(stop_event: threading.Event) -> None:
    """Print a '.' every 5 seconds during long API calls to show progress."""
    while not stop_event.is_set():
        print(".", end="", flush=True)
        time.sleep(5)


# ---------------------------------------------------------------------------
# Exclusion Helper (Additive)
# ---------------------------------------------------------------------------

def is_excluded(path: Path, exclusions: list[str], root: Path) -> bool:
    """
    True if path matches any exclusion rule.
    Rules may be:
      - directory names (e.g., '__pycache__', '.git')
      - filenames
      - wildcards (e.g., '*.pyc')
    """
    if not exclusions:
        return False

    rel_path = path.relative_to(root)
    rel_str = str(rel_path).replace("\\", "/").lower()

    for rule in exclusions:

        # wildcard (support deep patterns like **/.venv/**)
        if "*" in rule and fnmatch.fnmatch(rel_str, rule.lower()):
            return True


        # exact directory name
        if path.is_dir() and path.name.lower() == rule.lower():
            return True

        # exact filename
        if path.is_file() and path.name.lower() == rule.lower():
            return True

        # any ancestor directory
        if rule.lower() in [p.name.lower() for p in rel_path.parents]:
            return True

    return False


# ---------------------------------------------------------------------------
# File Utilities 
# ---------------------------------------------------------------------------

def find_file_anywhere(base_dir: Path, filename: str, exclusions: list[str]) -> Path | None:
    """
    Search recursively within base_dir for a file with the given name (case-insensitive).
    Allows minor variations in file name (e.g., singular vs plural, or one-character differences).
    Returns the first match found, or None if not found.
    """
    import difflib

    target = filename.lower()
    candidates = [
        p for p in base_dir.rglob("*")
        if not is_excluded(p, exclusions, base_dir)
    ]

    # Collect exact matches first
    exact_matches = [p for p in candidates if p.name.lower() == target]
    if exact_matches:
        if len(exact_matches) > 1:
            logging.warning(
                f"Multiple matches found for '{filename}' under {base_dir.name}: {exact_matches[0]} (and {len(exact_matches)-1} more)"
            )
        return exact_matches[0]

    # Allow near matches (singular/plural, typos, etc.)
    close_matches = []
    for p in candidates:
        score = difflib.SequenceMatcher(None, p.name.lower(), target).ratio()
        if score > 0.85:  # accept small differences
            close_matches.append((score, p))

    if close_matches:
        close_matches.sort(reverse=True, key=lambda x: x[0])
        best_match = close_matches[0][1]
        logging.warning(
            f"No exact match for '{filename}' under {base_dir.name}; using close match '{best_match.name}'"
        )
        return best_match

    return None


def combine_submission_text(student_dir: Path, required_files: list[str], exclusions: list[str]) -> str:
    """
    Combines submission text with wildcard + cardinality + escalation support.
    """
    parts = []

    for rule in required_files:
        pattern, min_c, max_c = parse_rule(rule)

        is_glob = any(ch in pattern for ch in ["*", "?"])

        matches = []
        escalation = "none"

        # ---------- Wildcard rules ----------
        if is_glob:
            matches = find_all_by_pattern(student_dir, pattern, exclusions)

        # ---------- Non-glob rules (filename expectations) ----------
        else:
            matches, escalation = find_with_escalation(
                student_dir,
                pattern,          # keep full relative path if provided
                exclusions,
                min_c
            )

        found = len(matches)
        ok = (found >= min_c) and (found <= max_c)
        status = "OK" if ok else "VIOLATION"

        logging.info(f"[RULE] {rule} → found {found} ({status}) escalation={escalation}")
        for m in matches:
            logging.info(f"       → {m.relative_to(student_dir)}")

        if not ok:
            high = "∞" if max_c == float("inf") else max_c
            logging.warning(
                f"Rule violated: {rule} — expected {min_c}..{high}, found {found}"
            )

        # Append contents
        for m in matches:
            try:
                parts.append(
                    f"\n\n### FILE START\n"
                    f"### RULE: {rule}\n"
                    f"### PATH: {m.relative_to(student_dir)}\n"
                    f"### MATCH TYPE: {escalation}\n\n"
                    f"{m.read_text(encoding='utf-8', errors='ignore')}"
                )
            except Exception as e:
                logging.warning(f"Could not read {m}: {e}")

    return "\n".join(parts)


def write_grade_summary(student_dir: Path, result_text: str) -> None:
    """Write detailed grade summary to grade_summary.txt inside the student folder."""
    out_file = student_dir / "grade_summary.txt"
    out_file.write_text(result_text, encoding="utf-8")
    logging.info(f"Wrote summary → {out_file}")


def append_csv_row(csv_path: Path, student_name: str, result_text: str | None, status: str) -> None:
    """
    Append a detailed grading record to grading_summary.csv.
    Extracts total points, possible points, and first deduction sentence if available.
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = csv_path.exists()
    total_points, possible_points, first_deduction = "", "", ""

    if result_text:
        
        # Example matches: "Total: 85/100", "Score: 90 out of 100"
        match = re.search(r"(\b\d{1,3}\b)\s*(?:/|out of)\s*(\b\d{1,3}\b)", result_text, re.IGNORECASE)
        if match:
            total_points, possible_points = match.group(1), match.group(2)
        # Extract first deduction sentence
        deductions = re.findall(r"^-.*", result_text, flags=re.MULTILINE)
        if not deductions:
            # If no bullets, use first sentence mentioning "point" or "deduct"
            deductions = re.findall(r"[^.]*?(?:point|deduct)[^.]*\.", result_text, re.IGNORECASE)
        if deductions:
            first_deduction = deductions[0].strip()

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "version", "Student Directory", "Status", "Points Earned", "Points Possible", "First Deduction"])
            
        writer.writerow([timestamp, __version__, student_name, status, total_points, possible_points, first_deduction])


# ---------------------------------------------------------------------------
# Bonus Inference (Option C+ : behavior only, no points)
# ---------------------------------------------------------------------------

def extract_bonus_behaviors_from_key(key_text: str) -> list[str]:
    """
    Extract bonus behavior text from answer key lines like:
      *** BONUS +2.5 points for ordering contacts by last name
    Returns a list of behavior strings, e.g.:
      ["ordering contacts by last name"]
    """
    behaviors = []
    pattern = re.compile(
        r"\*\*\*\s*BONUS\s*\+\d+(?:\.\d+)?\s*points?\s*for\s*(.+)",
        flags=re.IGNORECASE
    )
    for line in key_text.splitlines():
        m = pattern.search(line.strip())
        if m:
            behaviors.append(m.group(1).strip())
    return behaviors


def behavior_mentioned_in_text(behavior: str, text: str) -> bool:
    """
    Heuristic matcher: checks whether the LLM output plausibly mentions
    the behavior. Uses simple keyword overlap to stay robust and avoid
    heavy NLP dependencies.
    """
    # tokenize behavior into meaningful words
    tokens = [
        t for t in re.split(r"\W+", behavior.lower())
        if len(t) > 3
    ]
    tlow = text.lower()

    # accept if at least two meaningful tokens appear in the text,
    # or if the full behavior phrase is directly present
    if behavior.lower() in tlow:
        return True

    hits = sum(1 for t in tokens if t in tlow)
    return hits >= 2


def has_inferred_bonus_annotation(text: str) -> bool:
    return "includes inferred bonus" in text.lower()


def rewrite_score_summary_with_inferred_bonus(text: str, behavior: str) -> str:
    """
    Rewrites:
      Total: X/Y
    to:
      Total: X/Y (includes inferred bonus for <behavior>)
    Only touches the Score Summary line.
    """
    def repl(match):
        return f"{match.group(0)} (includes inferred bonus for {behavior})"

    return re.sub(
        r"Total:\s*\d+\s*(?:/|out of)\s*\d+",
        repl,
        text,
        count=1,
        flags=re.IGNORECASE
    )


def infer_bonus_if_needed(result_text: str, key_text: str, student_name: str | None = None) -> str:
    """
    Option C+:
    - If bonus behavior is detected in LLM output
    - BUT no '(includes ... bonus)' is present in Total
    → Append '(includes inferred bonus for <behavior>)' to Total line.
    """
    behaviors = extract_bonus_behaviors_from_key(key_text)
    if not behaviors:
        return result_text  # no bonus defined

    # If already annotated, do nothing
    if has_inferred_bonus_annotation(result_text) or "includes" in result_text.lower():
        return result_text

    # Detect whether any bonus behavior is mentioned
    for b in behaviors:
        if behavior_mentioned_in_text(b, result_text):
            updated = rewrite_score_summary_with_inferred_bonus(result_text, b)
            if updated != result_text:
                who = f" ({student_name})" if student_name else ""
                logging.warning(f"[INFERRED BONUS]{who} → {b} (no points assigned)")
                return updated

    return result_text






# ---------------------------------------------------------------------------
# Rule Parsing
# ---------------------------------------------------------------------------

import re

def parse_rule(rule: str):
    """
    Parse rules like:
      urls.py(2)
      urls.py(1..3)
      *.png(0..*)
      models.py

    Returns (pattern, min_count, max_count)
    """
    m = re.match(r"^(.+?)\((\d+)(?:\.\.(\*|\d+))?\)$", rule.strip())
    if not m:
        return rule, 1, 1   # default exactly 1

    pattern = m.group(1)
    min_count = int(m.group(2))
    max_raw = m.group(3)

    if max_raw in (None, "*"):
        max_count = float("inf")
    else:
        max_count = int(max_raw)

    return pattern, min_count, max_count

# ---------------------------------------------------------------------------
# Glob matcher (returns ALL)
# ---------------------------------------------------------------------------

def find_all_by_pattern(root: Path, pattern: str, exclusions: list[str]) -> list[Path]:
    """
    Match files using full relative paths, not just filenames.
    Supports patterns like:
      blogsite/**/urls.py
    """
    matches = []

    # Normalize pattern for cross-platform matching
    normalized = pattern.replace("\\", "/").lower()

    for path in root.rglob("*"):
        if is_excluded(path, exclusions, root):
            continue

        # Match using relative path from root
        rel = str(path.relative_to(root)).replace("\\", "/").lower()

        if fnmatch.fnmatch(rel, normalized):
            matches.append(path)

    return matches


# ---------------------------------------------------------------------------
# Escalating filename search (recursive + fuzz)
# ---------------------------------------------------------------------------

import difflib

def find_with_escalation(base_dir: Path, pattern: str, exclusions: list[str], needed: int):
    """
    Escalating search with PATH-AWARE matching:

      Phase 1a: Exact RELATIVE PATH match (if pattern contains directories)
      Phase 1b: Exact BASENAME match (recursive)
      Phase 2:  Pattern expansion (e.g., urls.py -> urls.*)
      Phase 3:  Fuzzy fallback (e.g., url.py)
    """
    import difflib

    results = []

    # Normalize pattern for comparison
    # e.g. "mycontacts/mycontacts/urls.py"
    raw = str(pattern).replace("\\", "/").strip().lower()
    has_path = "/" in raw

    # ---------- Phase 1a: exact RELATIVE PATH ----------
    if has_path:
        for p in base_dir.rglob("*"):
            if p.is_file() and not is_excluded(p, exclusions, base_dir):
                rel = str(p.relative_to(base_dir)).replace("\\", "/").lower()
                if rel == raw:
                    results.append(p)

        if len(results) >= needed:
            return results[:needed], "exact-path"
        
        if has_path and not results:
            logging.warning(f"[ESCALATION] Path not found: {pattern}. Falling back to basename search.")

    # Derive basename for next phases
    filename = Path(raw).name

    # ---------- Phase 1b: exact BASENAME ----------
    for p in base_dir.rglob("*"):
        if p.is_file() and not is_excluded(p, exclusions, base_dir):
            if p.name.lower() == filename:
                # avoid duplicates if Phase 1a already added something
                if p not in results:
                    results.append(p)

    if len(results) >= needed:
        return results[:needed], "exact-name"

    # ---------- Phase 2: pattern expansion (urls.py -> urls.*) ----------
    if filename.lower().endswith(".py"):
        expanded = filename[:-3] + ".*"
    else:
        expanded = filename + ".*"

    for p in find_all_by_pattern(base_dir, expanded, exclusions):
        if p not in results:
            results.append(p)

    if len(results) >= needed:
        return results[:needed], "pattern"

    # ---------- Phase 3: fuzzy filename ----------
    for p in base_dir.rglob("*"):
        if p.is_file() and not is_excluded(p, exclusions, base_dir):
            score = difflib.SequenceMatcher(None, p.name.lower(), filename).ratio()
            if score >= 0.85 and p not in results:
                results.append(p)

    if results:
        return results, "fuzzy"

    return [], "none"

def enforce_bonus_alignment(result_text: str) -> str:
    """
    If a Bonus Credit section exists and is not 'None',
    ensure the Score Summary acknowledges bonus existence.
    """
    if "**Bonus Credit" not in result_text:
        return result_text

    in_bonus = False
    lines = result_text.splitlines()
    bonuses = []

    for line in lines:
        if line.startswith("2. **Bonus Credit"):
            in_bonus = True
            continue
        if line.startswith("3. **"):
            break
        if in_bonus and line.strip().startswith("-"):
            bonuses.append(line.strip("- ").strip())

    if not bonuses:
        return result_text

    # Bonus earned but not acknowledged in score
    if "includes" not in result_text.lower():
        def repl(m):
            return f"{m.group(0)} (includes bonus credit)"

        return re.sub(
            r"Total:\s*\d+\s*/\s*\d+",
            repl,
            result_text,
            count=1
        )

    return result_text


def is_effectively_empty(student_dir: Path, exclusions: list[str]) -> bool:
    """
    Treat as empty if:
      - no files at all OR
      - only README.md (any casing) once exclusions are honored
    """
    readable_files = []
    for p in student_dir.rglob("*"):
        if p.is_file() and not is_excluded(p, exclusions, student_dir):
            readable_files.append(p)

    if not readable_files:
        return True

    # If all non-excluded files are README.md (any case), consider empty
    non_readme = [p for p in readable_files if p.name.lower() != "readme.md"]
    return len(non_readme) == 0


def enforce_base_max(result_text: str, base_max: int) -> str:
    """
    Force denominator to remain equal to base_max.
    """
    return re.sub(
        r"Total:\s*(\d+)\s*/\s*(\d+)",
        lambda m: f"Total: {m.group(1)}/{base_max}",
        result_text,
        count=1
    )

# ---------------------------------------------------------------------------
# Grading Logic (Prompt restored verbatim)
# ---------------------------------------------------------------------------

def grade_submission(
    student_dir: Path,
    key_file: Path,
    required_files: list[str],
    model: str,
    max_score: int,
    exclusions: list[str],
    system_prompt: str
) -> str | None:  
    
    """
    Grade a single student submission using the stored 'Coding Exercise Scoring' logic.
    Returns the plain-text feedback (or None on error).
    """
    try:
        key_text = key_file.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logging.error(f"Cannot read key file '{key_file}': {e}")
        return None

    combined_text = combine_submission_text(student_dir, required_files, exclusions)

    # -----------------------------
    # BUILD THE ACTUAL GRADING PROMPT (ORIGINAL)
    # -----------------------------
    prompt = f"""

{system_prompt}

Answer Key:
{key_text}

Student Submission:
{combined_text}

Respond using the following format:

1. **Deductions**
- List each deduction with brief explanation and points lost.

2. **Bonus Credit (if any)**
- List each bonus feature that was found and why it qualifies, in plain language.
- If no bonuses were earned, write "None".

3. **Strengths**
- Two sentences about what was done well.

4. **Areas for Improvement**
- Two sentences about what to work on.

5. **Score Summary**
- The base assignment maximum (DENOMINATOR) is {max_score}.
- Bonus points are added to the final score and MAY exceed the denominator.
- Format strictly as:
  - "Total: <earned>/{max_score} points (includes <bonus> bonus)" if bonus exists
  - Otherwise: "Total: <earned>/{max_score} points"
  - "Total: 75/60 points (includes 15 bonus)" would be valid

6. **Supportive Closing**
- One encouraging sentence to the student.
"""

    # Progress dots
    stop_event = threading.Event()
    thread = threading.Thread(target=idle_marker, args=(stop_event,), daemon=True)
    thread.start()

    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a grading assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        result_text = resp.choices[0].message["content"].strip()

        # Infer bonus behavior if LLM implied it but did not apply it to Total
        result_text = infer_bonus_if_needed(result_text, key_text, student_dir.name)

        # Enforce that Bonus section and Score Summary agree
        result_text = enforce_bonus_alignment(result_text)

        # Force denominator to remain base maximum
        result_text = enforce_base_max(result_text, max_score)

        write_grade_summary(student_dir, result_text)
        return result_text

    except APIError as e:
        logging.error(f"API error: {e}")
        return None
    except Exception as e:
        logging.exception(f"Error during grading for {student_dir.name}: {e}")
        return None
    finally:
        stop_event.set()
        thread.join(timeout=1)
        print("")  # newline after dots


# ---------------------------------------------------------------------------
# Main (Validate restored verbatim + exclusions applied)
# ---------------------------------------------------------------------------

def main() -> None:
    setup_logging()
    logs_dir = Path("logs")

    parser = argparse.ArgumentParser(description="Automated grader for coding assignments.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--skip-scored", action="store_true", help="Skip any student directory that already contains grade_summary.txt")
    parser.add_argument("--config", required=True, help="Path to configuration JSON.")
    parser.add_argument("--student", help="Only grade this specific student directory. Exact directory name match (case-insensitive).")
    parser.add_argument("--dry-run", action="store_true", help="List/check without API calls.")
   
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Verify config, key, API key, and grade ONLY the first matching folder."
    )

    parser.add_argument(
        "--repo-root",
        required=True,
        help="Path to the folder containing all student repositories."
    )

    parser.add_argument(
        "--system-prompt",
        default="prompts/base_system_prompt.txt",
        help="Path to system-level grading prompt file."
    )

    args = parser.parse_args()

    # Resolve and validate repo root
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        logging.error(f"--repo-root does not exist or is not a directory: {repo_root}")
        logging.error("Example: --repo-root D:/Exercises/FA25/ITEC660/Lab05")
        sys.exit(1)

    cfg = load_config(args.config)
    # Global (deployment-wide) config – may specify default model, etc.
    global_cfg = load_global_config()

    # Base maximum score for this assignment (denominator, before any bonus)
    max_score = int(cfg.get("max_score", 60))
    logging.info(f"[CONFIG] Base max_score = {max_score}")


    # Resolve system prompt path
    system_prompt_path = Path(args.system_prompt)

    if not system_prompt_path.is_absolute():
        project_root = Path(__file__).resolve().parent
        system_prompt_path = (project_root / system_prompt_path).resolve()

    if not system_prompt_path.exists():
        logging.error(f"System prompt file not found: {system_prompt_path}")
        sys.exit(1)

    system_prompt = system_prompt_path.read_text(encoding="utf-8")


    assignment_pattern = cfg.get("assignment_pattern", "homework-*")


    # Resolve key file from ./keys directory (project repo, next to this script)
    project_root = Path(__file__).resolve().parent
    keys_dir = project_root / "keys"
    key_file = (keys_dir / cfg["key_file"]).resolve()


    required_files = list(cfg.get("required_files", []))

    # ---- build exclusions from profiles + assignment ----
    base_exclusions = list(cfg.get("exclusions", []))
    profiles = list(cfg.get("language_profile", []))

    # Load global exclusions library
    excl_path = Path("configs/exclusions.json")
    global_exclusions = {}
    if excl_path.exists():
        global_exclusions = json.loads(excl_path.read_text(encoding="utf-8"))

    # Start with global defaults
    exclusions = list(global_exclusions.get("global", []))

    # Add language profiles (e.g., python, web, java)
    for p in profiles:
        exclusions.extend(global_exclusions.get(p, []))

    # Finally, add assignment-specific overrides
    exclusions.extend(base_exclusions)

    # gpt-5 is the backup value in case nothing is specified in global config,
    model = global_cfg.get("model", "gpt-5")

    dry_run = args.dry_run 

    # Environment setup
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("Missing OPENAI_API_KEY environment variable.")
        sys.exit(1)

    openai.api_key = api_key

    if not key_file.exists():
        logging.error(f"Key file not found in keys/: {key_file}")
        logging.error("Expected directory structure:")
        logging.error("  <project_root>/keys/<key_file>")
        sys.exit(1)

    # Collect student directories from repo root
    root = repo_root
    student_dirs = [d for d in root.glob(assignment_pattern) if d.is_dir()]


    if not student_dirs:
        logging.error(f"No student directories found for pattern '{assignment_pattern}'.")
        sys.exit(1)

    # Optional filter for one student
    if args.student:
        wanted = args.student.strip().lower()
        student_dirs = [s for s in student_dirs if s.name.lower() == wanted]
        if not student_dirs:
            logging.error(f"No directory found matching '{args.student}'.")
            sys.exit(1)
        logging.info(f"Running for single student: {student_dirs[0].name}")

    # Optional skip for already-scored submissions
    if args.skip_scored:
        before = len(student_dirs)
        student_dirs = [
            s for s in student_dirs
            if not (s / "grade_summary.txt").exists()
        ]
        skipped = before - len(student_dirs)
        logging.info(f"--skip-scored enabled → skipped {skipped} already-graded folder(s)")

    # Validation mode (restored behavior)
    if args.validate:
        if not student_dirs:
            logging.warning("--skip-scored removed all folders; nothing left to validate.")
            return

        first = student_dirs[0]

        logging.info("---- VALIDATION START ----")
        logging.info(f"Config OK: {args.config}")
        logging.info(f"API key detected: YES")
        logging.info(f"Key file exists: {key_file}")
        logging.info(f"Model configured: {model}")
        logging.info(f"First matching folder: {first.name}")

        for rule in required_files:
            pattern, min_c, max_c = parse_rule(rule)

            is_glob = any(ch in pattern for ch in ["*", "?"])

            # ---------- Glob rules (supports wildcards + cardinality) ----------
            if is_glob:
                matches = find_all_by_pattern(first, pattern, exclusions)
                found = len(matches)

                if min_c <= found <= max_c:
                    logging.info(f"[VALIDATE] Found: {rule}")
                else:
                    logging.warning(f"[VALIDATE] Missing or invalid count for: {rule} (found {found})")
                continue

            # ---------- Non-glob rules (original behavior) ----------
            expected = first / pattern
            if expected.exists() and not is_excluded(expected, exclusions, first):
                logging.info(f"[VALIDATE] Found: {rule}")
            elif find_file_anywhere(first, Path(pattern).name, exclusions):
                logging.warning(f"[VALIDATE] {rule} misplaced but found elsewhere.")
            else:
                logging.warning(f"[VALIDATE] Missing required file: {rule}")

        csv_path = logs_dir / "grading_summary.csv"
        if dry_run:
            logging.info("[VALIDATE] Dry-run is enabled; skipping API call.")
            append_csv_row(csv_path, first.name, "Validated (dry-run)", "Validate run")
            logging.info("---- VALIDATION COMPLETE (DRY) ----")
            return

        logging.info(f"[VALIDATE] Grading ONLY: {first.name} ...")
        result_text = grade_submission(
            first, 
            key_file,
            required_files, 
            model,
            max_score,
            exclusions, 
            system_prompt
        )
        status = "Graded" if result_text else "Error"
        append_csv_row(csv_path, first.name, result_text, f"Validate run: {status}")
        logging.info("---- VALIDATION COMPLETE ----")
        return

    # Dry-run listing
    if dry_run:
        logging.info("Dry run mode: listing directories only (no API calls).")
        for s in student_dirs:
            print(s)
        csv_path = logs_dir / "grading_summary.csv"
        if not csv_path.exists():
            with csv_path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["Student Directory", "Status"])
        return

    # Full grading
    logging.info(f"Found {len(student_dirs)} student directories for pattern '{assignment_pattern}'.")
    csv_path = logs_dir / "grading_summary.csv"
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Student Directory", "Status"])

    for sdir in student_dirs:

        # Skip empty or README-only submissions
        if is_effectively_empty(sdir, exclusions):
            logging.info(f"Skipping empty/README-only directory: {sdir.name}")

            # Optional: write a minimal grade_summary.txt so it’s auditable
            summary = (
                "Submission not graded.\n"
                "Reason: folder is empty or contains only README.md.\n"
            )
            write_grade_summary(sdir, summary)

            # Also record in CSV
            append_csv_row(logs_dir / "grading_summary.csv", sdir.name, None, "Empty/README-only")
            continue

        logging.info(f"Grading {sdir.name} ...")
        result_text = grade_submission(
            sdir, 
            key_file,
            required_files, 
            model,
            max_score,
            exclusions, 
            system_prompt
        )
        
        status = "Graded" if result_text else "Error"
        append_csv_row(csv_path, sdir.name, result_text, status)

    logging.info("Grading completed.")
    logging.info(f"Results consolidated → {csv_path}")

if __name__ == "__main__":
    main()
