from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.base import get_db
from models.user import User
from core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token. Bypasses auth if no token (dev mode)."""
    # If no token provided, return a default user for development
    if not token:
        # Get or create a default user for development
        default_user = db.query(User).filter(User.email == "dev@example.com").first()
        if not default_user:
            # Create a default dev user if it doesn't exist
            from core.security import get_password_hash
            default_user = User(
                email="dev@example.com",
                hashed_password=get_password_hash("dev123")
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
        return default_user
    """Get current authenticated user from JWT token."""
    # #region agent log
    import json
    import os
    log_path = "/Users/pratikkumar/Desktop/Antenna Designer/.cursor/debug.log"
    try:
        log_data = {"location": "dependencies.py:11", "message": "GET_CURRENT_USER_START", "data": {"has_token": bool(token), "token_preview": token[:20] + "..." if token and len(token) > 20 else token}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        pass
    # #endregion
    
    try:
        payload = decode_access_token(token)
        # #region agent log
        try:
            log_data = {"location": "dependencies.py:21", "message": "DECODE_TOKEN_SUCCESS", "data": {"payload_keys": list(payload.keys()), "user_id": payload.get("sub")}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        user_id: int = payload.get("sub")
        if user_id is None:
            # #region agent log
            try:
                log_data = {"location": "dependencies.py:27", "message": "USER_ID_MISSING", "data": {}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}
                with open(log_path, "a") as f:
                    f.write(json.dumps(log_data) + "\n")
            except Exception:
                pass
            # #endregion
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            # #region agent log
            try:
                log_data = {"location": "dependencies.py:35", "message": "USER_NOT_FOUND", "data": {"user_id": user_id}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}
                with open(log_path, "a") as f:
                    f.write(json.dumps(log_data) + "\n")
            except Exception:
                pass
            # #endregion
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        # #region agent log
        try:
            log_data = {"location": "dependencies.py:43", "message": "GET_CURRENT_USER_SUCCESS", "data": {"user_id": user.id, "email": user.email}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        return user
    except HTTPException:
        raise
    except Exception as e:
        # #region agent log
        try:
            log_data = {"location": "dependencies.py:51", "message": "GET_CURRENT_USER_ERROR", "data": {"error": str(e), "error_type": type(e).__name__}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "E"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


