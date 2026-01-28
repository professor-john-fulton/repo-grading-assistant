# OpenAI API Setup Guide

Complete guide for setting up OpenAI API access for the Repo Grading Assistant.

---

## Prerequisites

- Credit/debit card for API billing (even if using free credits)
- Email address
- Phone number for verification

---

## Step 1: Create OpenAI Account

### Sign Up

1. Go to https://platform.openai.com/signup
2. Choose sign-up method:
   - **Email + password** (recommended)
   - **Google account**
   - **Microsoft account**
3. Verify your email address
4. Complete phone verification (SMS code)

**Note:** If you already have a ChatGPT account, you can use the same credentials.

---

## Step 2: Set Up Billing

### Add Payment Method

1. Navigate to https://platform.openai.com/account/billing/overview
2. Click **"Add payment method"**
3. Enter credit/debit card information
4. Complete verification

### Set Spending Limits (Highly Recommended)

1. Go to https://platform.openai.com/account/limits
2. Set **"Monthly budget"**:
   - For testing: $5-10
   - For regular use (30 students): $10-20/month
   - Adjust based on your needs
3. Enable **"Spending limit email notifications"**
4. Set alert thresholds (e.g., 50%, 75%, 90%)

**Why set limits?**
- Prevents unexpected charges from bugs or runaway processes
- You'll get email alerts as you approach limits
- Billing stops automatically when limit reached

---

## Step 3: Create API Key

### Generate New Key

1. Navigate to https://platform.openai.com/api-keys
2. Click **"+ Create new secret key"**
3. (Optional) Give it a descriptive name: e.g., "Grading Assistant - Jan 2026"
4. **Important:** Copy the key immediately - you won't see it again!
   - Starts with `sk-proj-` (new format) or `sk-` (old format)
   - Save securely (password manager recommended)

### Key Permissions

For grading assistant, default permissions are fine:
- ✓ Read access
- ✓ Write access (for API calls)

**Security Note:** Never commit API keys to git or share them publicly.

---

## Step 4: Configure Model Access

### Check Model Availability

1. Go to https://platform.openai.com/settings/organization/general
2. Navigate to model permissions/limits section
   - **Note:** OpenAI's dashboard changes frequently; if you can't find this, try:
     - Settings → Organization → Limits
     - Settings → Usage & billing → Limits
     - Use ChatGPT to help locate: "Where do I enable model access in OpenAI dashboard?"

### Enable Required Models

**Default model for this tool:** `gpt-5-mini`

**If you see "Model not accessible" errors:**

1. Check your account tier:
   - **Free tier** (with credits): Limited model access
   - **Pay-as-you-go**: Access to most models
   - **Enterprise**: Full access

2. Verify model access:
   ```bash
   python -c "
   import openai
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   openai.api_key = os.getenv('OPENAI_API_KEY')
   
   models = openai.Model.list()
   available = [m.id for m in models.data]
   print('Available models:', available)
   print()
   print('gpt-5-mini available:', 'gpt-5-mini' in available)
   "
   ```

3. **If model not available:**
   - Upgrade to pay-as-you-go tier
   - Contact OpenAI support
   - Use alternative model (e.g., `gpt-4.1`)

---

## Step 5: Install API Key Locally

### Option 1: .env File (Recommended for Development)

**Create .env file in project root:**

```bash
cd repo-grading-assistant
nano .env  # or use any text editor
```

**Add your API key:**

```
OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

**Security checklist:**
- ✓ `.env` file is in `.gitignore` (already included)
- ✓ Never commit `.env` to version control
- ✓ Don't share `.env` file
- ✓ Use different keys for different projects/environments

---

### Option 2: Environment Variable (For Production/CI)

**Linux/macOS (add to ~/.bashrc or ~/.zshrc):**

```bash
export OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

**Windows PowerShell (persistent):**

```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-proj-your-actual-key-here', 'User')
```

**Windows Command Prompt (session only):**

```cmd
set OPENAI_API_KEY=sk-proj-your-actual-key-here
```

**Verify it's set:**

```bash
echo $OPENAI_API_KEY  # Linux/macOS/Git Bash
echo %OPENAI_API_KEY%  # Windows CMD
$env:OPENAI_API_KEY   # PowerShell
```

---

## Step 6: Verify Setup

### Test API Connection

```bash
# Activate your virtual environment
source .venv/Scripts/activate  # Git Bash
# or
.\.venv\Scripts\Activate.ps1   # PowerShell

# Test with validation command
repo-grading-assistant \
  --config docs/examples/grading_config_example.json \
  --repo-root docs/examples/grading_assignment_example \
  --validate
```

**Expected output:**
```
🎓 Repository Grading Assistant v1.0.10
...
Found 2 student repositories
Processing: student_1
  ✓ Required files found: 6/6
  ⚙ Calling OpenAI API with gpt-5-mini...
  ✓ Grade: XX/60
```

**If you see errors, see [Troubleshooting](#troubleshooting) below.**

---

## Understanding Costs

### Pricing Structure (as of January 2026)

**gpt-5-mini (default model):**
- **Input:** ~$0.075 per 1M tokens
- **Output:** ~$0.30 per 1M tokens

**What's a token?**
- Roughly 4 characters or ¾ of a word
- A typical assignment might be 5,000-20,000 tokens (student code + prompts)

### Cost Estimation

**Small assignment (calculator, simple script):**
- Input: ~3,000 tokens
- Output: ~1,000 tokens
- **Cost per student:** ~$0.001-0.003

**Medium assignment (web app, Django project):**
- Input: ~10,000 tokens  
- Output: ~2,000 tokens
- **Cost per student:** ~$0.005-0.015

**Large assignment (complex multi-file project):**
- Input: ~30,000 tokens
- Output: ~3,000 tokens
- **Cost per student:** ~$0.020-0.050

**For a class of 30 students:**
- Small assignment: ~$0.03-0.09
- Medium assignment: ~$0.15-0.45
- Large assignment: ~$0.60-1.50

**Cost-saving tips:**
1. Use aggressive exclusions (node_modules, build files)
2. Use gpt-5-mini instead of gpt-5 or gpt-4
3. Test with --validate (one student) before full run
4. Set monthly spending limits

---

## Model Selection

### Available Models

| Model | Speed | Cost | Quality | Best For |
|-------|-------|------|---------|----------|
| gpt-5-mini | Fast | Low | Good | Default choice for most assignments |
| gpt-5 | Medium | Medium | Excellent | Complex code, advanced features |
| gpt-5-nano | Fastest | Lowest | Basic | Simple assignments, tight budgets |
| gpt-4.1 | Slow | High | Very Good | Legacy option |
| gpt-4o-mini | Fast | Medium | Good | Alternative to gpt-5-mini |

### Configuring Model

**Global configuration (`configs/global_config.json`):**

```json
{
  "model": "gpt-5-mini"
}
```

**Per-assignment override:**

```json
{
  "assignment_pattern": "lab-5-*",
  "grading_key_file": "lab5_key.txt",
  "model": "gpt-5",
  "max_score": 60
}
```

See [Model Configuration](../README.md#model-configuration) for details.

---

## Monitoring Usage

### View Usage Dashboard

1. Go to https://platform.openai.com/usage
2. See current month's usage
3. Filter by date range
4. Export usage data

### Set Up Alerts

1. Go to https://platform.openai.com/account/limits
2. Enable email notifications
3. Set alert thresholds (50%, 75%, 90% of budget)

### Track Usage in Code

```python
# usage_tracker.py
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# After grading
response = openai.ChatCompletion.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "test"}],
    max_completion_tokens=10
)

# Check token usage
usage = response.usage
print(f"Tokens used:")
print(f"  Input: {usage.prompt_tokens}")
print(f"  Output: {usage.completion_tokens}")
print(f"  Total: {usage.total_tokens}")
```

---

## Security Best Practices

### API Key Management

**Do:**
- ✓ Use environment variables or .env files
- ✓ Add `.env` to `.gitignore`
- ✓ Use different keys for dev/prod
- ✓ Rotate keys periodically (every 3-6 months)
- ✓ Store keys in password manager
- ✓ Delete unused keys

**Don't:**
- ✗ Commit keys to git
- ✗ Share keys via email/chat
- ✗ Hard-code keys in scripts
- ✗ Use same key for all projects
- ✗ Store keys in plain text files

### If Your Key Is Compromised

**Immediate actions:**

1. **Revoke the key:**
   - Go to https://platform.openai.com/api-keys
   - Find the compromised key
   - Click "Revoke" or "Delete"

2. **Check usage:**
   - Go to https://platform.openai.com/usage
   - Look for unexpected usage
   - Contact OpenAI support if you see unauthorized charges

3. **Create new key:**
   - Generate a new API key
   - Update your `.env` file
   - Update any deployment environments

4. **Review security:**
   - Check git history: `git log -p | grep -i "sk-proj"`
   - Check for exposed keys: https://github.com/settings/tokens
   - Update passwords if needed

---

## Troubleshooting

### Error: "Incorrect API key provided"

**Causes:**
- Key copied incorrectly (missing characters)
- Key revoked or deleted
- Typo in .env file

**Solutions:**

1. **Verify key format:**
   ```bash
   # Should start with sk-proj- or sk-
   cat .env
   ```

2. **Test key directly:**
   ```bash
   python -c "
   import openai
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   key = os.getenv('OPENAI_API_KEY')
   print(f'Key starts with: {key[:10]}...' if key else 'Key not found')
   
   openai.api_key = key
   try:
       models = openai.Model.list()
       print('✓ API key is valid')
   except Exception as e:
       print(f'✗ API key error: {e}')
   "
   ```

3. **Regenerate if needed:**
   - Go to https://platform.openai.com/api-keys
   - Create new key
   - Update .env file

---

### Error: "You exceeded your current quota"

**Cause:** You've hit your spending limit or used all free credits.

**Solutions:**

1. **Check billing:**
   - Go to https://platform.openai.com/account/billing/overview
   - Verify payment method is valid
   - Check if you have available balance

2. **Increase budget:**
   - Go to https://platform.openai.com/account/limits
   - Increase monthly budget
   - Note: May take a few minutes to update

3. **Wait for reset:**
   - If using free credits, they may reset monthly
   - Usage limits reset at start of each billing period

---

### Error: "Rate limit reached"

**Cause:** Making too many API requests too quickly.

**Solutions:**

1. **Wait and retry:**
   - Free tier: Lower rate limits
   - Pay-as-you-go: Higher limits
   - Enterprise: Highest limits

2. **Batch processing:**
   - Grade students in smaller batches
   - Add delays between batches (see [Advanced Usage](ADVANCED_USAGE.md))

3. **Upgrade tier:**
   - Go to https://platform.openai.com/account/billing/overview
   - Upgrade to pay-as-you-go for higher limits

---

### Error: "Model not found" or "does not have access"

**Cause:** Your API key doesn't have access to the requested model.

**Solutions:**

1. **Check model name:**
   ```json
   {
     "model": "gpt-5-mini"  // Verify spelling
   }
   ```

2. **List available models:**
   ```bash
   python -c "
   import openai
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   openai.api_key = os.getenv('OPENAI_API_KEY')
   
   models = openai.Model.list()
   available = sorted([m.id for m in models.data])
   print('Available models:')
   for model in available:
       print(f'  - {model}')
   "
   ```

3. **Use alternative model:**
   - Update config to use available model
   - See [Model Selection](#model-selection)

---

## Additional Resources

### Official Documentation

- **OpenAI Platform Overview:** https://platform.openai.com/docs/overview
- **API Reference:** https://platform.openai.com/docs/api-reference
- **Pricing:** https://openai.com/api/pricing/
- **Rate Limits:** https://platform.openai.com/docs/guides/rate-limits
- **Best Practices:** https://platform.openai.com/docs/guides/production-best-practices

### Tool Documentation

- [README.md](../README.md) - Main documentation
- [QUICKSTART.md](../QUICKSTART.md) - Quick setup guide
- [FAQ](../README.md#faq) - Common questions
- [INSTALLATION_TROUBLESHOOTING.md](INSTALLATION_TROUBLESHOOTING.md) - Setup issues

### Support

**OpenAI Support:**
- Help Center: https://help.openai.com
- Community Forum: https://community.openai.com
- Email: support@openai.com

**Tool Support:**
- GitHub Issues: https://github.com/professor-john-fulton/repo-grading-assistant/issues
- Email: john.fulton2@franklin.edu

---

## Next Steps

Once your API is set up:

1. ✓ [Run validation test](../QUICKSTART.md#validate-configuration)
2. ✓ [Try example data](EXAMPLES_WALKTHROUGH.md)
3. ✓ [Grade your first assignment](../README.md#quick-start)
4. ✓ [Learn advanced workflows](ADVANCED_USAGE.md)

**Happy grading!** 🎓
