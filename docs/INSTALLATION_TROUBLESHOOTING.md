# Installation Troubleshooting

This guide helps resolve common installation and setup issues with the Repo Grading Assistant.

---

## Table of Contents

- [Python Version Issues](#python-version-issues)
- [Virtual Environment Problems](#virtual-environment-problems)
- [Package Installation Errors](#package-installation-errors)
- [OpenAI API Key Issues](#openai-api-key-issues)
- [Path and Permission Errors](#path-and-permission-errors)
- [Module Not Found Errors](#module-not-found-errors)
- [Platform-Specific Issues](#platform-specific-issues)

---

## Python Version Issues

### Error: "Python 3.11+ required"

**Symptom:**
```
ERROR: This package requires Python 3.11+
```

**Cause:** Wrong Python version installed or activated.

**Solution:**

**Check your Python version:**
```bash
python --version
# or
py --version
```

**Windows - Install Python 3.11+:**
1. Download from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Verify installation: `py -3.11 --version`

**macOS - Using Homebrew:**
```bash
brew install python@3.11
python3.11 --version
```

**Linux - Using apt:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
python3.11 --version
```

---

### Error: "py: command not found" (Windows)

**Symptom:**
```bash
bash: py: command not found
```

**Cause:** Python launcher not installed or not in PATH.

**Solution:**

**Option 1 - Use python directly:**
```bash
python --version  # Check if this works
python -m venv .venv
```

**Option 2 - Add Python to PATH:**
1. Open "Environment Variables" in Windows Settings
2. Edit "Path" variable
3. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\`
4. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts\`
5. Restart terminal

**Option 3 - Reinstall Python with launcher:**
- Download Python installer from python.org
- Check "Install launcher for all users"
- Check "Add Python to PATH"

---

### Multiple Python Versions Conflict

**Symptom:**
```
wrong version activates when I run python
```

**Cause:** Multiple Python installations competing.

**Solution:**

**Use specific version explicitly:**

**Windows:**
```bash
py -3.11 -m venv .venv
```

**macOS/Linux:**
```bash
python3.11 -m venv .venv
```

**Check which Python is being used:**
```bash
which python     # macOS/Linux
where python     # Windows
```

---

## Virtual Environment Problems

### Error: Virtual environment won't activate

**Symptom:**
```bash
source .venv/Scripts/activate  # Nothing happens
# or
.venv: command not found
```

**Cause:** Wrong activation command for your shell.

**Solution:**

**Git Bash (Windows):**
```bash
source .venv/Scripts/activate
```

**PowerShell (Windows):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**If PowerShell gives execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

**Command Prompt (Windows):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Verify activation:**
```bash
which python     # Should show .venv path
python --version # Should show correct version
```

---

### Error: "cannot create virtual environment"

**Symptom:**
```
Error: Command '...' returned non-zero exit status 1
```

**Cause:** Missing `venv` module or permissions issue.

**Solution:**

**Install venv module (Linux/macOS):**
```bash
# Debian/Ubuntu
sudo apt install python3.11-venv

# macOS
# (usually included with Python installation)
```

**Check permissions:**
```bash
# Make sure you have write access to current directory
ls -la
pwd
```

**Try with full path:**
```bash
python3.11 -m venv .venv
```

---

### Error: Virtual environment exists but broken

**Symptom:**
```
ImportError: No module named 'pip'
```

**Cause:** Corrupted virtual environment.

**Solution:**

**Delete and recreate:**

**Windows (PowerShell):**
```powershell
Remove-Item -Recurse -Force .venv
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
```

**Reinstall packages:**
```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

---

## Package Installation Errors

### Error: "pip: command not found"

**Symptom:**
```bash
pip install ...
bash: pip: command not found
```

**Cause:** Virtual environment not activated or pip not installed.

**Solution:**

**Activate virtual environment first:**
```bash
source .venv/Scripts/activate  # Git Bash (Windows)
# or
.\.venv\Scripts\Activate.ps1   # PowerShell
```

**Use python -m pip instead:**
```bash
python -m pip install -U pip
```

---

### Error: "Could not find a version that satisfies the requirement"

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement package-name
```

**Cause:** Package not available for your Python version, or network issue.

**Solution:**

**Check Python version compatibility:**
```bash
python --version  # Make sure it's 3.11+
```

**Update pip:**
```bash
python -m pip install --upgrade pip
```

**Check internet connection:**
```bash
python -m pip install --index-url https://pypi.org/simple/ openai
```

**Try with verbose output:**
```bash
python -m pip install -v -e ".[dev]"
```

---

### Error: "error: Microsoft Visual C++ 14.0 or greater is required" (Windows)

**Symptom:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Cause:** Missing C++ build tools (some Python packages need compilation).

**Solution:**

**Option 1 - Install Build Tools:**
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Restart terminal
4. Retry installation

**Option 2 - Use pre-built wheels:**
```bash
python -m pip install --only-binary :all: package-name
```

---

### Error: "Permission denied" during installation

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
```

**Cause:** Installing to system Python instead of virtual environment, or no write permissions.

**Solution:**

**Ensure virtual environment is activated:**
```bash
# You should see (.venv) in your prompt
which python  # Should point to .venv
```

**Don't use sudo:**
```bash
# WRONG:
sudo pip install ...

# RIGHT:
python -m pip install ...
```

**Check directory permissions:**
```bash
# macOS/Linux
ls -la .venv
chmod -R u+w .venv

# Windows (PowerShell as Administrator)
icacls .venv /grant:r "$env:USERNAME:(OI)(CI)F" /T
```

---

## OpenAI API Key Issues

### Error: "OPENAI_API_KEY not set"

**Symptom:**
```
ValueError: OPENAI_API_KEY not set
```

**Cause:** Environment variable not configured.

**Solution:**

**Create .env file in project root:**
```bash
# Navigate to project root
cd repo-grading-assistant

# Copy example
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Add your API key:**
```
OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

**Verify it loads:**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key found!' if os.getenv('OPENAI_API_KEY') else 'Key missing!')"
```

---

### Error: ".env file not loading"

**Symptom:**
Key is in .env but tool still says "not set"

**Cause:** Running from wrong directory or .env not in project root.

**Solution:**

**Check current directory:**
```bash
pwd  # Should be the project root
ls .env  # File should exist
```

**Verify .env format:**
```bash
cat .env
# Should show: OPENAI_API_KEY="sk-proj-..."
# No spaces around =
# Quotes optional but recommended
```

**Install python-dotenv:**
```bash
python -m pip install python-dotenv
```

---

### Error: "Incorrect API key provided"

**Symptom:**
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Cause:** Invalid or expired API key, or typo.

**Solution:**

**Verify key format:**
- Should start with `sk-proj-` (new format) or `sk-` (old format)
- No spaces or line breaks
- Complete key copied

**Check key on OpenAI platform:**
1. Go to https://platform.openai.com/api-keys
2. Verify key is still active
3. Regenerate if necessary

**Test key directly:**
```bash
python -c "
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
print(f'Key (first 10 chars): {openai.api_key[:10]}...')

try:
    models = openai.Model.list()
    print('✓ API key is valid')
except Exception as e:
    print(f'✗ API key error: {e}')
"
```

---

## Path and Permission Errors

### Error: "No such file or directory: grading_config.json"

**Symptom:**
```
FileNotFoundError: No such file or directory: 'grading_config.json'
```

**Cause:** Running command from wrong directory or wrong path.

**Solution:**

**Check current directory:**
```bash
pwd
ls  # List files in current directory
```

**Use absolute path:**
```bash
repo-grading-assistant --config /full/path/to/grading_config.json
```

**Use relative path correctly:**
```bash
# If config is in docs/examples:
repo-grading-assistant --config docs/examples/grading_config_example.json

# If you're already in docs/examples:
repo-grading-assistant --config grading_config_example.json
```

---

### Error: "Permission denied" writing output files

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: 'logs/grading.log'
```

**Cause:** No write permissions in current directory.

**Solution:**

**Check directory permissions:**
```bash
# macOS/Linux
ls -la
# You should have write (w) permission

# Windows
icacls .
```

**Create logs directory manually:**
```bash
mkdir logs
```

**Run from writable location:**
```bash
cd ~/Documents/grading  # Move to a location you own
```

---

### Error: "repo-grading-assistant: command not found"

**Symptom:**
```bash
repo-grading-assistant --help
bash: repo-grading-assistant: command not found
```

**Cause:** Package not installed or Scripts folder not in PATH.

**Solution:**

**Verify installation:**
```bash
python -m pip list | grep repo-grading-assistant
```

**Reinstall in editable mode:**
```bash
python -m pip install -e ".[dev]"
```

**Check Scripts directory in PATH:**

**Windows (PowerShell):**
```powershell
$env:PATH -split ';' | Select-String "Scripts"
```

**Add to PATH if needed:**
```powershell
$env:PATH += ";$PWD\.venv\Scripts"
```

**Alternative - Run as module:**
```bash
python -m repo_grading_assistant.cli --help
```

---

## Module Not Found Errors

### Error: "ModuleNotFoundError: No module named 'repo_grading_assistant'"

**Symptom:**
```
ModuleNotFoundError: No module named 'repo_grading_assistant'
```

**Cause:** Package not installed or wrong Python environment active.

**Solution:**

**Verify virtual environment active:**
```bash
which python  # Should show .venv path
```

**Install package:**
```bash
python -m pip install -e ".[dev]"
```

**Verify installation:**
```bash
python -c "import repo_grading_assistant; print(repo_grading_assistant.__version__)"
```

---

### Error: "ModuleNotFoundError: No module named 'openai'"

**Symptom:**
```
ModuleNotFoundError: No module named 'openai'
```

**Cause:** Dependencies not installed.

**Solution:**

**Install all dependencies:**
```bash
python -m pip install -e ".[dev]"
```

**Or install openai specifically:**
```bash
python -m pip install openai
```

**Verify:**
```bash
python -c "import openai; print(openai.__version__)"
```

---

## Platform-Specific Issues

### Windows: Line ending issues

**Symptom:**
Scripts have `^M` characters or don't run

**Cause:** Git converting line endings incorrectly.

**Solution:**

**Configure Git:**
```bash
git config --global core.autocrlf true
```

**Re-clone repository:**
```bash
cd ..
rm -rf repo-grading-assistant
git clone https://github.com/professor-john-fulton/repo-grading-assistant.git
```

---

### macOS: "command not found" after installation

**Symptom:**
```bash
repo-grading-assistant: command not found
```

**Cause:** Shell not finding Scripts directory.

**Solution:**

**Add to PATH in shell config:**

**For zsh (default on macOS):**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**For bash:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
```

---

### Linux: SSL certificate errors

**Symptom:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Cause:** Missing or outdated SSL certificates.

**Solution:**

**Update certificates:**
```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install --reinstall ca-certificates

# Fedora/RHEL
sudo yum reinstall ca-certificates
```

**Upgrade certifi package:**
```bash
python -m pip install --upgrade certifi
```

---

## Still Having Issues?

### Collect Diagnostic Information

Run these commands and include output when asking for help:

```bash
# System information
python --version
pip --version
which python

# Package information
python -m pip list

# Environment check
env | grep -i python

# Test imports
python -c "import sys; print(sys.path)"
python -c "import repo_grading_assistant; print(repo_grading_assistant.__version__)"

# Check installation
python -m pip show repo-grading-assistant
```

### Get Help

- **GitHub Issues:** https://github.com/professor-john-fulton/repo-grading-assistant/issues
- **Include:**
  - Full error message
  - Commands you ran
  - Output of diagnostic commands above
  - Your OS and Python version

### Related Documentation

- [README.md](../README.md) - Main documentation
- [QUICKSTART.md](../QUICKSTART.md) - Setup guide
- [FAQ](../README.md#faq) - Common questions
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development setup
