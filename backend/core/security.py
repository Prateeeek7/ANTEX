from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import bcrypt

from core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash. Handles both passlib and direct bcrypt hashes."""
    # #region agent log
    import json
    import os
    log_path = "/Users/pratikkumar/Desktop/Antenna Designer/.cursor/debug.log"
    try:
        log_data = {"location": "security.py:14", "message": "VERIFY_PASSWORD_START", "data": {"plain_len": len(plain_password), "hash_len": len(hashed_password), "hash_preview": hashed_password[:20] if hashed_password else None}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        pass
    # #endregion
    
    # Ensure password is <= 72 bytes (bcrypt limit)
    password_bytes = plain_password.encode('utf-8')[:72]
    plain_password_truncated = password_bytes.decode('utf-8', errors='ignore')
    
    # Try passlib first (for passlib-formatted hashes)
    try:
        result = pwd_context.verify(plain_password_truncated, hashed_password)
        # #region agent log
        try:
            log_data = {"location": "security.py:24", "message": "VERIFY_PASSWORD_RESULT", "data": {"result": result, "method": "passlib"}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        return result
    except Exception:
        # If passlib fails, try direct bcrypt verification
        try:
            # Direct bcrypt hash verification
            password_utf8_bytes = plain_password.encode('utf-8')[:72]
            hash_bytes = hashed_password.encode('utf-8')
            result = bcrypt.checkpw(password_utf8_bytes, hash_bytes)
            # #region agent log
            try:
                log_data = {"location": "security.py:34", "message": "VERIFY_PASSWORD_RESULT", "data": {"result": result, "method": "bcrypt_direct"}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
                with open(log_path, "a") as f:
                    f.write(json.dumps(log_data) + "\n")
            except Exception:
                pass
            # #endregion
            return result
        except Exception as e:
            # #region agent log
            try:
                log_data = {"location": "security.py:42", "message": "VERIFY_PASSWORD_ERROR", "data": {"error": str(e), "error_type": type(e).__name__}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
                with open(log_path, "a") as f:
                    f.write(json.dumps(log_data) + "\n")
            except Exception:
                pass
            # #endregion
            return False


def get_password_hash(password: str) -> str:
    """Hash a password. Automatically truncates to 72 bytes if needed (bcrypt limit)."""
    # #region agent log
    import json
    import os
    log_path = "/Users/pratikkumar/Desktop/Antenna Designer/.cursor/debug.log"
    try:
        log_data = {"location": "security.py:18", "message": "PASSWORD_HASH_START", "data": {"password_type": type(password).__name__, "password_str_len": len(password), "password_bytes_len": len(password.encode('utf-8')) if password else 0}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        pass
    # #endregion
    
    # Bcrypt has a 72 byte limit, truncate if necessary
    # Convert to bytes to check actual byte length
    password_bytes = password.encode('utf-8')
    original_byte_len = len(password_bytes)
    
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        password_bytes = password_bytes[:72]
        # Try to decode, but if it fails at the end, remove bytes until it works
        # This handles multi-byte UTF-8 characters at the boundary
        while True:
            try:
                password = password_bytes.decode('utf-8')
                break
            except UnicodeDecodeError:
                if len(password_bytes) == 0:
                    raise ValueError("Password cannot be hashed")
                password_bytes = password_bytes[:-1]
    
    # #region agent log
    try:
        final_password_bytes = password.encode('utf-8')
        log_data = {"location": "security.py:38", "message": "PASSWORD_BEFORE_HASH", "data": {"final_str_len": len(password), "final_bytes_len": len(final_password_bytes), "original_bytes_len": original_byte_len}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        pass
    # #endregion
    
    # Now password is guaranteed to be <= 72 bytes
    # Ensure we pass a string that's exactly <= 72 bytes when encoded
    # Passlib will convert to bytes internally, so this should work
    # But first, let's ensure the string itself, when encoded, is <= 72 bytes
    final_password_bytes = password.encode('utf-8')
    if len(final_password_bytes) > 72:
        # This shouldn't happen, but double-check
        final_password_bytes = final_password_bytes[:72]
        password = final_password_bytes.decode('utf-8', errors='ignore')
    
    # Ensure password is exactly <= 72 bytes when encoded to UTF-8
    # This is the bcrypt limit
    password_utf8_bytes = password.encode('utf-8')
    if len(password_utf8_bytes) > 72:
        password_utf8_bytes = password_utf8_bytes[:72]
        password = password_utf8_bytes.decode('utf-8', errors='ignore')
    
    try:
        # Try passlib first (preferred method)
        result = pwd_context.hash(password)
        # #region agent log
        try:
            log_data = {"location": "security.py:72", "message": "PASSWORD_HASH_SUCCESS", "data": {"hash_created": bool(result), "method": "passlib"}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        return result
    except (ValueError, Exception) as e:
        # If passlib fails, fall back to direct bcrypt
        # #region agent log
        try:
            log_data = {"location": "security.py:82", "message": "PASSWORD_HASH_PASSLIB_FAILED", "data": {"error": str(e), "error_type": type(e).__name__, "falling_back_to_bcrypt": True}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        
        # Fallback: use bcrypt directly
        # Ensure password is bytes and <= 72 bytes
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        result = hashed.decode('utf-8')
        
        # #region agent log
        try:
            log_data = {"location": "security.py:94", "message": "PASSWORD_HASH_SUCCESS", "data": {"hash_created": bool(result), "method": "bcrypt_direct"}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        return result


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    # #region agent log
    import json
    import os
    log_path = "/Users/pratikkumar/Desktop/Antenna Designer/.cursor/debug.log"
    try:
        log_data = {"location": "security.py:177", "message": "DECODE_TOKEN_START", "data": {"token_preview": token[:30] + "..." if len(token) > 30 else token, "jwt_secret_len": len(settings.JWT_SECRET), "algorithm": settings.JWT_ALGORITHM}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        pass
    # #endregion
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        # #region agent log
        try:
            log_data = {"location": "security.py:188", "message": "DECODE_TOKEN_SUCCESS", "data": {"payload_keys": list(payload.keys()), "user_id": payload.get("sub")}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        return payload
    except JWTError as e:
        # #region agent log
        try:
            log_data = {"location": "security.py:196", "message": "DECODE_TOKEN_JWT_ERROR", "data": {"error": str(e), "error_type": type(e).__name__}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

