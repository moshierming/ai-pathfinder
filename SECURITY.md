# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.1.x   | ✅ Active           |
| < 1.1   | ❌ Not supported    |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT open a public issue**
2. Email: [moshierming@gmail.com](mailto:moshierming@gmail.com)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact

We will acknowledge receipt within 48 hours and provide a fix timeline within 7 days.

## Security Measures

This project implements the following security practices:

- **XSS Prevention**: All LLM-generated content is escaped via `html.escape()` before rendering
- **Input Validation**: Goal text (1000 chars), import file size (2MB), profile decode (50KB)
- **No Secrets in Code**: API keys are managed via Streamlit secrets or environment variables
- **Dependency Scanning**: Regular review of dependencies for known vulnerabilities
- **CI/CD**: Automated testing on every push (Python 3.10/3.11/3.12)
