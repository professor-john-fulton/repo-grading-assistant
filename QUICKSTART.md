# Quickstart Guide

> If you haven't installed yet, see [README.md](README.md) → Installation.

## 1. Set Up OpenAI API Key

You will need an OpenAI paid account to run this project (except for pytest suite, `--help`, and `--dry-run` commands).

1. Create an OpenAI account and set up billing at https://platform.openai.com/
2. Generate an API key: https://platform.openai.com/api-keys
3. **IMPORTANT:** Ensure your API key has access to the model you plan to use (default: `gpt-5-mini`)
   - Model access is configured per project/API key in OpenAI's dashboard
   - If your key doesn't have access to the model, you'll get an error: "The API project does not have access to model gpt-5-mini"
   - See OpenAI's project settings to enable specific models for your API key
4. Copy the `.env.example` file to create your own `.env` file:
   ```bash
   cp .env.example .env
   ```
5. Edit the `.env` file and replace the placeholder with your actual API key:
   ```
   OPENAI_API_KEY="sk-proj-your-actual-key-here"
   ```

> **Security:** The `.env` file is excluded from git by `.gitignore` to keep your API key secure. Never commit your actual API key.
>
> **Developer Note:** Configuring which models an OpenAI API key can access can be challenging through the OpenAI dashboard. The settings are typically found in your project's settings under model permissions or limits. If you have trouble locating these settings, you may need to use ChatGPT or contact OpenAI support to help navigate to the correct configuration page.

---

## 2. Set Up Grading Files

### Grading Keys Directory

Create a `./keys/` directory at the project root to store your assignment grading templates:

```bash
mkdir keys
```

You can use `./docs/examples/grading_key_example.txt` as a reference for creating your own grading key files.

### Configuration Files

Create assignment configuration files in the `./configs/` directory. You can use `./docs/examples/grading_config_example.json` as a reference.

---

## 3. Run Example Commands

### Dry Run (no API calls)

```bash
repo-grading-assistant \
  --config docs/examples/grading_config_example.json \
  --repo-root docs/examples/grading_assignment_example \
  --dry-run
```

### Validate Configuration

```bash
repo-grading-assistant \
  --config docs/examples/grading_config_example.json \
  --repo-root docs/examples/grading_assignment_example \
  --validate
```

### Run Full Grading

```bash
repo-grading-assistant \
  --config docs/examples/grading_config_example.json \
  --repo-root docs/examples/grading_assignment_example
```

---

## Critical Rules

**⚠️ DO NOT rename the project folder after creating `.venv`**

- Always use `python -m pip`, not `pip`
- Activate venv every session

### Why This Matters

Editable installs (`pip install -e .`) hard-code absolute paths. Renaming or moving the folder breaks the launcher scripts.

### Recovery: If You Renamed/Moved the Folder

```bash
deactivate
rm -rf .venv
python -m venv .venv
source .venv/Scripts/activate   # Git Bash
# or: .\.venv\Scripts\Activate.ps1   # PowerShell
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

### Verification

```bash
which python
python -c "import sys; print(sys.executable)"
repo-grading-assistant --help
```

---

## Common Errors

### Fatal error in launcher

**Cause:** Project folder was renamed or moved after creating virtual environment.

**Fix:** Follow the recovery steps above.

### Module not found

**Cause:** Virtual environment not activated.

**Fix:** Run `source .venv/Scripts/activate` (Git Bash) or `.\.venv\Scripts\Activate.ps1` (PowerShell)

### API key error

**Cause:** `.env` file missing or `OPENAI_API_KEY` not set.

**Fix:** Ensure `.env` file exists in project root with your API key.


2) Generate an API key and put it somewhere safe. This should help: https://platform.openai.com/docs/quickstart  Setup the key to have access to the gpt-5 model.

3) The key should be a project key string of the form "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" (this isn't a real key). Put the key in a .env file at the top level of the project.
```
OPENAI_API_KEY="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" 
```



You may create a ./keys/ directory  at the base level. Use ./docs/examples/grading_key_example.txt to create an example key file

In the ./configs/ directory, you should create  ./docs/examples/grading_config_example.json to create an example config file



🔒 Critical rules (put in bold in docs)

DO NOT rename the project folder after creating .venv

Always use python -m pip, not pip

Activate venv every session

Recovery section (short but powerful)

If you renamed/moved the folder:

deactivate
rm -rf .venv
python -m venv .venv
source .venv/Scripts/activate   # or bin/activate
python -m pip install -e .

Optional verification
which python
python -c "import sys; print(sys.executable)"
repo-grading-assistant --help

Why this matters (1-liner)

Editable installs hard-code absolute paths.
Renaming breaks launchers.

Mentor suggestion

Add a "Common Errors" section with:

Fatal error in launcher

PATH conflicts

Multiple Python installs