# COMENTARIO DE ARCHIVO - GRAPHHIRED
# Funciones de seguridad. Partes: sanitizacion, validacion de archivos, hash/verificacion de password, creacion de JWT y resolucion del usuario autenticado.

"""
Security and Sanitization Module
OWASP-compliant data sanitization
"""
import re
import bleach
from typing import Any, Dict
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.entities import User

# Allowed HTML tags (minimal for safety)
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

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


def hash_password(password: str) -> str:
    """Hash a plaintext password before persistence."""
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT for API authentication."""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from a Bearer token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise JWTError("Missing subject")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    user = db.query(User).filter(User.email == str(email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
