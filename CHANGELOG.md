# Changelog

## 1.1.0 - 3/4/2026

- Move version source to top-level VERSION.py and wire package metadata to read from it.
- Load VERSION.py safely when running from source to keep CLI version reporting consistent.
- Relocate example configs/keys to top-level configs/ and keys/ with updated paths in docs.
- Add a strict example config and clarify manual test commands.
- Fix global config resolution to avoid configs/configs nesting.
- Add retry logic for transient OpenAI connection/timeouts during grading.
- edits to wildcard student file location matching





