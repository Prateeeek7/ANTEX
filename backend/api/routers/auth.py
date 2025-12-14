from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from db.base import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, Token
from core.security import get_password_hash, verify_password, create_access_token
from core.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # #region agent log
    import json
    import os
    log_path = "/Users/pratikkumar/Desktop/Antenna Designer/.cursor/debug.log"
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log_data = {"location": "auth.py:15", "message": "REGISTER_ENDPOINT_CALLED", "data": {"email": user_data.email, "password_length": len(user_data.password) if user_data.password else 0}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "C"}
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception as e:
        import logging
        logging.error(f"Debug log write failed: {e}")
    # #endregion
    try:
        # Validate password length (minimum)
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Note: Password will be automatically truncated to 72 bytes in get_password_hash
        # if it exceeds bcrypt's limit
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        # Hash password (will auto-truncate if needed)
        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            email=user_data.email.lower(),
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # #region agent log
        try:
            log_data = {"location": "auth.py:48", "message": "REGISTER_SUCCESS", "data": {"user_id": new_user.id, "email": new_user.email}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        
        return new_user
    except HTTPException as e:
        # #region agent log
        try:
            log_data = {"location": "auth.py:50", "message": "REGISTER_HTTP_ERROR", "data": {"status_code": e.status_code, "detail": str(e.detail)}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        raise
    except Exception as e:
        # #region agent log
        try:
            log_data = {"location": "auth.py:56", "message": "REGISTER_EXCEPTION", "data": {"error_type": type(e).__name__, "error_message": str(e)}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token."""
    # #region agent log
    import json
    import os
    log_path = "/Users/pratikkumar/Desktop/Antenna Designer/.cursor/debug.log"
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log_data = {"location": "auth.py:63", "message": "LOGIN_ENDPOINT_CALLED", "data": {"username": form_data.username, "has_password": bool(form_data.password), "password_length": len(form_data.password) if form_data.password else 0}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "C"}
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception as e:
        import logging
        logging.error(f"Debug log write failed: {e}")
    # #endregion
    # OAuth2PasswordRequestForm uses 'username' field, but we store email
    user = db.query(User).filter(User.email == form_data.username).first()
    # #region agent log
    try:
        log_data = {"location": "auth.py:67", "message": "LOGIN_USER_LOOKUP", "data": {"user_found": user is not None, "user_id": user.id if user else None}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        pass
    # #endregion
    password_valid = False
    if user:
        password_valid = verify_password(form_data.password, user.hashed_password)
    if not user or not password_valid:
        # #region agent log
        try:
            log_data = {"location": "auth.py:72", "message": "LOGIN_FAILED", "data": {"user_exists": user is not None, "password_valid": password_valid}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
            with open(log_path, "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception:
            pass
        # #endregion
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    )
    
    # #region agent log
    try:
        log_data = {"location": "auth.py:80", "message": "LOGIN_SUCCESS", "data": {"user_id": user.id, "token_created": bool(access_token)}, "timestamp": int(__import__("time").time() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "D"}
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "\n")
    except Exception:
        pass
    # #endregion
    
    return {"access_token": access_token, "token_type": "bearer"}

