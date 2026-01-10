# Release Checklist

-   [ ] python -m pytest
-   [ ] git status clean
-   [ ] confirm .gitignore blocks outputs
-   [ ] git ls-files \| grep -E
    "(grade_summary\|grading_summary\|keys/)" returns nothing
-   [ ] bump version
-   [ ] tag release
-   [ ] git push github main --tags
