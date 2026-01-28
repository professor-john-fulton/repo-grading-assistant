# Contributing to Repo Grading Assistant
Contributing.md


Thanks for your interest!

This project is maintained by a solo maintainer. Contributions are
welcome, but please keep scope focused and changes well-documented.

The standard flow for contribution to this open source project is:
fork remotely → clone your fork locally → branch → change → test (install/usage) → push → PR back to upstream

## Setup

Go to the upstream repo page - https://github.com/professor-john-fulton/repo-grading-assistant

Click Fork (top right).

Create the fork under your GitHub account.

Result: you now have https://github.com/<your-username>/repo-grading-assistant.

Clone your fork locally
``` bash
git clone https://github.com/<your-username>/repo-grading-assistant.git
cd repo-grading-assistant
git remote -v
```

Add the upstream remote (so you can sync later):
``` bash
git remote add upstream https://github.com/professor-john-fulton/repo-grading-assistant.git
git remote -v
```

Create a topic branch
``` bash
git checkout main
git pull --ff-only origin main
git checkout -b working-branch
```


Use QUICKSTART.md for how to run the project. It is strongly suggested that you run the provided pytest suite before beginning  to make changes.

Make change and add tests as needed


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

``` bash
git status
```

Examine changes and confirm that only those changes you intend are reflected


add and commit changes to your change branch
``` bash
git add -A
git commit -m "description of change"
```

Push the changed brach
``` bash
git push -u origin working-branch
```

Open a Pull Request (PR) back to the upstream repo

Go to your fork on GitHub.

You'll see a banner offering to Compare & Pull Request for your pushed branch → click it.

Set:

base repository: professor-john-fulton/repo-grading-assistant

base: main

head repository: your fork

compare: working-branch

In the PR description, include:

What you changed (brief)

What you tested (e.g., “Ran --dry-run + --validate per README; clarified step X”)


8) If upstream changes while you work: sync your fork
git checkout main
git fetch upstream
git merge upstream/main
git push origin main


Then rebase or merge your branch onto updated main (pick one):

git checkout working-branch
git rebase main
# or: git merge main
git push --force-with-lease   # only if you rebased

9) After PR feedback: update the same PR

Just commit more changes to the same branch and push again:

# edit README.md
git add -A
git commit -m "clarify installation step"
git push


The PR updates automatically.





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
