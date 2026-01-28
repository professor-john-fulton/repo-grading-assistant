# Security Policy

## Supported Versions

Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security issue, please report it responsibly:

**Contact:** john.fulton2@franklin.edu

**Please include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Important:** Please do NOT open a public issue for security problems.

## Response

This is a best-effort open source project maintained by volunteers. You will receive acknowledgement when possible, typically within 7 days.

## Security Best Practices

When using this tool:

### API Key Protection
- **Never commit** your `.env` file or API keys to version control
- Store API keys securely using environment variables or `.env` files
- Rotate API keys periodically
- Use project-specific API keys with limited permissions

### Data Handling
- **Never commit** student submissions, grade outputs, or logs to version control
- Review `.gitignore` before committing to ensure sensitive files are excluded
- Be aware that student code is sent to OpenAI's API for processing
- Inform students about AI processing per your institution's policies

### Local Security
- Keep your Python environment updated
- Review dependencies regularly for known vulnerabilities
- Run the tool in a dedicated virtual environment
- Limit file system permissions for the logs directory

### OpenAI API Security
- Enable spending limits on your OpenAI account
- Monitor API usage regularly
- Use separate API keys for development and production
- Review OpenAI's security best practices: https://platform.openai.com/docs/guides/safety-best-practices
