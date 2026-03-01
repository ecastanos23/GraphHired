"""
Security and Sanitization Module
OWASP-compliant data sanitization
"""
import re
import bleach
from typing import Any, Dict

# Allowed HTML tags (minimal for safety)
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}

def sanitize_text(text: str) -> str:
    """
    Sanitize text input to prevent XSS and injection attacks
    OWASP compliant sanitization
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    
    # Remove potential SQL injection patterns
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)",
        r"(--)",
        r"(;.*$)",
        r"(/\*.*\*/)",
    ]
    for pattern in sql_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    # Trim whitespace
    text = text.strip()
    
    return text

def sanitize_email(email: str) -> str:
    """Validate and sanitize email"""
    if not email:
        return ""
    
    email = email.strip().lower()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    return email

def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize dictionary values"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_text(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_text(item) if isinstance(item, str) else item 
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized

def validate_file_type(filename: str, allowed_extensions: list = None) -> bool:
    """Validate file extension"""
    if allowed_extensions is None:
        allowed_extensions = ['pdf', 'doc', 'docx', 'txt']
    
    if not filename:
        return False
    
    extension = filename.rsplit('.', 1)[-1].lower()
    return extension in allowed_extensions
