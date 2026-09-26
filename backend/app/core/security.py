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

try:
    import bcrypt
    _has_bcrypt = True
except ImportError:
    _has_bcrypt = False

from app.core.config import settings
from app.database.connection import get_db

# OAuth2 password bearer configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_password_hash(password: str) -> str:
    """Generate secure salted password hash using native bcrypt (with PBKDF2 fallback)."""
    if _has_bcrypt:
        try:
            pwd_bytes = password.encode("utf-8")[:72]
            return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")
        except Exception:
            pass
    # Reliable PBKDF2-HMAC-SHA256 fallback
    salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
    return f"pbkdf2:{salt}:{hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify raw password against stored hash (supports native bcrypt and legacy PBKDF2)."""
    if not hashed_password or not plain_password:
        return False
    if hashed_password.startswith("pbkdf2:"):
        parts = hashed_password.split(":")
        if len(parts) == 3:
            salt = parts[1]
            stored_hash = parts[2]
            computed = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
            return hmac.compare_digest(stored_hash, computed)
    if _has_bcrypt and (hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$")):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
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


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """FastAPI dependency: Extract and verify current active user from DB."""
    from app.models.user import User

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account no longer exists",
        )
    return user


def require_role(allowed_roles: List[str]):
    """Role-Based Access Control (RBAC) dependency factory."""
    async def role_checker(current_user=Depends(get_current_user)):
        user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: required role in {allowed_roles}, your role is {user_role}",
            )
        return current_user
    return role_checker
