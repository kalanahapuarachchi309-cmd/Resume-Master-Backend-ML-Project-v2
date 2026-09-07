"""Security, Hashing, and JWT Authentication Subsystem (Kalana)."""
import os
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db

# OAuth2 password bearer configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Try to use passlib for bcrypt, with a robust fallback
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    _has_passlib = True
except Exception:
    _has_passlib = False


def get_password_hash(password: str) -> str:
    """Generate secure salted password hash."""
    if _has_passlib:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    # Reliable PBKDF2-HMAC-SHA256 fallback
    salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
    return f"pbkdf2:{salt}:{hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify raw password against stored hash."""
    if hashed_password.startswith("pbkdf2:"):
        parts = hashed_password.split(":")
        if len(parts) == 3:
            salt = parts[1]
            stored_hash = parts[2]
            computed = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
            return hmac.compare_digest(stored_hash, computed)
    if _has_passlib:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
    return False


def create_access_token(subject: Any, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generate encoded JWT with subject, role, and expiration timestamp."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": str(role),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Validate signature and decode JWT payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


async 