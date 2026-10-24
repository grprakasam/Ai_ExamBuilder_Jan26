from typing import Optional
import uuid
from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db, SessionLocal
from app.models.user import User
from app.models.test import Test
from app.models.exam_attempt import ExamAttempt
from app.services.access_code_service import AccessCodeService

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/access-token", auto_error=False)

def get_current_user(db: Session = Depends(get_db), token: Optional[str] = Depends(reusable_oauth2)) -> User:
    if not token:
        raise HTTPException(401, "Sign in required")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = uuid.UUID(payload["sub"])
    except (JWTError, KeyError, ValueError, TypeError):
        raise HTTPException(401, "Invalid access token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "Unknown user")
    return user

def get_admin(current_user: User = Depends(get_current_user)):
    if current_user.email.lower() not in {e.lower() for e in settings.ADMIN_EMAILS}:
        raise HTTPException(403, "Administrator access required")
    return current_user

def session_hash(request: Request):
    return AccessCodeService.create_session_hash(
        request.client.host if request.client else "unknown", request.headers.get("user-agent", "unknown")
    )

def authorize_test(db: Session, test_id: uuid.UUID, access_code: Optional[str]):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(404, "Test not found")
    from datetime import datetime
    if not access_code or test.access_code != access_code.replace("-", "").upper() or not test.is_active:
        raise HTTPException(403, "Valid test access code required")
    if test.code_expiration and test.code_expiration < datetime.now():
        raise HTTPException(403, "Access code expired")
    return test

def require_test_access(test_id: uuid.UUID, db: Session = Depends(get_db),
                        x_access_code: Optional[str] = Header(None)):
    return authorize_test(db, test_id, x_access_code)

def authorize_attempt(db: Session, test_id: uuid.UUID, attempt_id: uuid.UUID, request: Request):
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id, ExamAttempt.test_id == test_id).first()
    if not attempt or attempt.session_hash != session_hash(request):
        raise HTTPException(403, "Attempt does not belong to this session")
    if attempt.is_completed:
        raise HTTPException(409, "Attempt already completed")
    return attempt
