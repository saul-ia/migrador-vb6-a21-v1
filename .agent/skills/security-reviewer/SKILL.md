---
name: security-reviewer
description: Automated OWASP-based security audit for migrated code. Scans for vulnerabilities in frontend/backend.
---

# Security Reviewer Skill v1.0

## Purpose

Automated security checks for code generated during VB6 → Angular migration.
Follows OWASP Top 10 guidelines adapted for Angular + Express + SQLite stack.

## When to Use

Run after Phase 3 (frontend generation) or as part of Phase 5 (quality gates).

## Security Rules

### Critical (Block Deployment)

| ID | Rule | Detection Pattern |
|----|------|-------------------|
| SEC-001 | No `innerHTML` with user input | `innerHTML`, `bypassSecurityTrustHtml` |
| SEC-002 | No `eval()` or `Function()` | `eval(`, `new Function(` |
| SEC-003 | No hardcoded secrets | API keys, passwords, tokens in source |
| SEC-004 | No raw SQL queries | `db.$queryRaw`, `db.$executeRaw`, `.query(` |
| SEC-005 | CORS properly configured | Wildcard `*` origin in production |
| SEC-006 | JWT expiration required | Tokens without `expiresIn` |
| SEC-007 | No `console.log` with sensitive data | Logging passwords, tokens, PII |
| SEC-008 | HTTPS enforced in production | HTTP URLs in production config |

### Warning (Review Required)

| ID | Rule | Detection Pattern |
|----|------|-------------------|
| SEC-W01 | Input validation on all endpoints | Missing `express-validator` |
| SEC-W02 | Rate limiting on auth endpoints | Missing `express-rate-limit` |
| SEC-W03 | Helmet.js middleware | Missing `helmet` in Express |
| SEC-W04 | CSRF protection | Missing CSRF token handling |
| SEC-W05 | File upload restrictions | Unrestricted `multer` config |

## Usage

```bash
python .agent/skills/security-reviewer/scripts/security_audit.py \
  --frontend ${OUTPUT_DIR}/apps/frontend/src \
  --backend ${OUTPUT_DIR}/apps/backend/src \
  --output ${ANALYSIS_DIR}/security-report.json \
  --html ${ANALYSIS_DIR}/SECURITY_REPORT.html
```

## Output

- `${ANALYSIS_DIR}/security-report.json` — Machine-readable results
- `${ANALYSIS_DIR}/SECURITY_REPORT.html` — Visual HTML report
