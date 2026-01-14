from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/access-token",
    auto_error=False
)

from app.db.session import get_db

def get_current_user(
    db: Session = Depends(get_db), 
    token: Optional[str] = Depends(reusable_oauth2)
) -> User:
    """
    MODIFIED: Always returns a default 'Demo Student' user to bypass login.
    """
    user = db.query(User).filter(User.email == "demo@student.com").first()
    if not user:
        user = User(
            email="demo@student.com",
            full_name="Demo Student",
            hashed_password="demo",
            grade_level=5
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
