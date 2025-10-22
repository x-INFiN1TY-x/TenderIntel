# Security Policy

## **🔒 Supported Versions**

We release security updates for the following versions of TenderIntel:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## **🚨 Reporting a Vulnerability**

The TenderIntel team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### **How to Report**

**DO NOT** create public GitHub issues for security vulnerabilities.

**Instead, report security issues privately to:**

📧 **security@tenderintel.org**

### **What to Include**

Please provide the following information:

1. **Type of vulnerability** (e.g., SQL injection, XSS, authentication bypass)
2. **Location** (file path, URL, or affected component)
3. **Step-by-step reproduction** instructions
4. **Proof of concept** or exploit code (if available)
5. **Potential impact** and affected systems
6. **Suggested remediation** (if you have ideas)

### **Response Timeline**

- **24 hours:** Acknowledgment of your report
- **72 hours:** Initial assessment and severity classification
- **7 days:** Detailed response with fix timeline
- **30 days:** Security patch release (for critical vulnerabilities)

### **Responsible Disclosure**

We kindly ask that you:
- ✅ Give us reasonable time to fix the issue before public disclosure
- ✅ Make a good faith effort to avoid privacy violations and data destruction
- ✅ Do not exploit the vulnerability beyond necessary demonstration
- ✅ Do not access or modify data that doesn't belong to you

## **🏆 Security Researchers Hall of Fame**

We recognize and thank security researchers who help us improve TenderIntel's security:

*(To be added as vulnerabilities are responsibly disclosed and fixed)*

## **🛡️ Security Best Practices**

### **For Users:**

**Authentication (When Implemented):**
- Use strong, unique passwords (minimum 12 characters)
- Enable two-factor authentication if available
- Rotate API keys regularly (every 90 days)
- Never share credentials or API keys

**Data Security:**
- Limit access to sensitive tender data
- Use HTTPS in production (never HTTP)
- Implement network firewalls
- Regular security audits of your deployment

**API Security:**
- Implement rate limiting (recommended: 100 req/min)
- Use API keys for authentication
- Monitor for unusual access patterns
- Log all API requests for audit trail

### **For Developers:**

**Code Security:**
- Follow OWASP Top 10 guidelines
- Validate all user inputs
- Sanitize SQL queries (parameterized queries only)
- Escape HTML output to prevent XSS
- Use type hints and validation (Pydantic)

**Dependency Security:**
- Run `pip audit` regularly
- Keep dependencies updated
- Review security advisories
- Use `dependabot` for automated updates

**Data Security:**
- Never log sensitive data (passwords, keys, personal info)
- Use environment variables for secrets
- Implement proper access controls
- Encrypt sensitive data at rest

## **🔍 Known Security Considerations**

### **Current Status (v1.0.0):**

**✅ Implemented:**
- Input validation with Pydantic models
- SQL injection protection (parameterized queries)
- CORS configuration for controlled access
- Error messages without sensitive information
- Rate limiting architecture (not enforced)

**⚠️ To Be Implemented:**
- User authentication and authorization
- API key management
- Role-based access control (RBAC)
- Audit logging
- Rate limiting enforcement

### **Data Privacy:**

**What We Store:**
- Government procurement data (public information)
- Search queries and analytics (for improving service)
- No personal identification information (PII)
- No payment information

**What We Don't Store:**
- User passwords (when auth implemented, use bcrypt + salt)
- Credit card or financial information
- Personal documents or files
- Social security or government ID numbers

## **🚀 Security Features**

### **Input Validation:**
```python
# All API endpoints use Pydantic for validation
class SearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=50)
    limit: int = Field(25, ge=1, le=100)
    
# This prevents:
# - SQL injection (parameterized queries)
# - XSS attacks (input sanitization)
# - Buffer overflows (length limits)
```

### **SQL Injection Protection:**
```python
# ✅ SAFE: Parameterized queries
cursor.execute("SELECT * FROM tenders WHERE tender_id = ?", (tender_id,))

# ❌ UNSAFE: String interpolation (never do this)
cursor.execute(f"SELECT * FROM tenders WHERE tender_id = '{tender_id}'")
```

### **CORS Configuration:**
```python
# Configure CORS appropriately for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## **📋 Security Checklist for Deployment**

### **Pre-Production Security:**

- [ ] **Change default configurations** (ports, hosts, credentials)
- [ ] **Enable HTTPS** with valid SSL certificates
- [ ] **Implement authentication** and authorization
- [ ] **Enable rate limiting** (100 requests/minute recommended)
- [ ] **Configure CORS** with specific allowed origins
- [ ] **Set up monitoring** and alerting
- [ ] **Enable audit logging** for all API requests
- [ ] **Implement backup** and disaster recovery
- [ ] **Security scan** with tools like `bandit`, `safety`
- [ ] **Penetration testing** before public deployment

### **Production Security:**

- [ ] **Regular updates:** Apply security patches within 7 days
- [ ] **Monitor logs:** Daily review of access logs
- [ ] **Audit trail:** Track all data modifications
- [ ] **Backup verification:** Weekly backup testing
- [ ] **Access review:** Quarterly permission audits
- [ ] **Dependency scan:** Monthly security updates
- [ ] **Incident response:** Plan in place and tested

## **🔐 Cryptography**

### **Sensitive Data Handling:**

**Database Encryption (When Needed):**
```python
# For sensitive procurement data (if required)
from cryptography.fernet import Fernet

# Generate key (store securely in env variable)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted = cipher.encrypt(b"sensitive data")

# Decrypt
decrypted = cipher.decrypt(encrypted)
```

**Password Hashing (For Future Auth):**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("user_password")

# Verify password
is_valid = pwd_context.verify("user_password", hashed)
```

## **⚙️ Security Configuration**

### **Environment Variables:**

```bash
# Required for production
export TENDERINTEL_SECRET_KEY="your-secret-key-here"
export TENDERINTEL_API_KEY_SALT="your-salt-here"

# AWS S3 (if using document storage)
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"

# Database encryption (if needed)
export DATABASE_ENCRYPTION_KEY="your_encryption_key"
```

### **Recommended Security Headers:**

```python
# Add to FastAPI middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

## **📊 Security Monitoring**

### **What to Monitor:**

- Failed authentication attempts (when implemented)
- Unusual API usage patterns
- Large data exports
- Repeated 403/401 errors
- Database connection errors
- Slow response times (potential DoS)

### **Recommended Tools:**

- **Application:** Sentry for error tracking
- **Infrastructure:** Prometheus + Grafana for metrics
- **Logs:** ELK stack or CloudWatch
- **Security:** OSSEC or Wazuh for intrusion detection

## **🆘 Incident Response**

### **If You Discover a Vulnerability:**

1. **Stop:** Don't exploit further
2. **Document:** Take notes on reproduction steps
3. **Report:** Email security@tenderintel.org immediately
4. **Wait:** Give us time to fix before disclosure
5. **Coordinate:** Work with us on responsible disclosure

### **If We Notify You:**

1. **Review:** Understand the vulnerability details
2. **Update:** Apply security patches immediately
3. **Verify:** Test that the fix resolves the issue
4. **Monitor:** Watch for exploitation attempts
5. **Learn:** Review your security practices

## **📚 Security Resources**

**OWASP Resources:**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [API Security Project](https://owasp.org/www-project-api-security/)
- [Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

**Python Security:**
- [Bandit Security Linter](https://github.com/PyCQA/bandit)
- [Safety Dependency Scanner](https://pyup.io/safety/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

**Government Security Standards:**
- India's IT Act 2000
- Information Technology (Reasonable Security Practices) Rules 2011
- CERT-In Guidelines

---

## **✅ Security Commitment**

The TenderIntel team is committed to:

- Responding promptly to security reports
- Fixing critical vulnerabilities within 7 days
- Transparent communication about security issues
- Regular security audits and testing
- Following industry best practices

**Thank you for helping keep TenderIntel and our users safe!**

---

**Security Contact:** security@tenderintel.org  
**PGP Key:** (To be published)  
**Last Updated:** October 22, 2025  
**Version:** 1.0
