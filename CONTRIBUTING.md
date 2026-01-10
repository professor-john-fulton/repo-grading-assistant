# Contributing to Repo Grading Assistant

Thanks for your interest!

This project is maintained by a solo maintainer. Contributions are
welcome, but please keep scope focused and changes well-documented.

## Setup

``` bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate     # Windows

pip install -e .[dev]
```

## Testing

``` bash
python -m pytest
```

## Style

-   Follow existing patterns
-   Keep functions small and testable
-   Lint with:

``` bash
ruff check .
```

## Pull Requests

-   Describe *why* the change is needed
-   Include tests where appropriate
-   Keep PRs small and focused

## Data Safety

Never commit: - student submissions - grade outputs - logs - API keys -
real configuration files

Use anonymized examples only.

------------------------------------------------------------------------

By contributing, you agree your work may be released under the MIT
license.
