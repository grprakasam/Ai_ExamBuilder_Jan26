from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api import deps
from app.services.access_code_service import AccessCodeService
from app.models.test import Test
from app.models.exam_attempt import ExamAttempt, AttemptRequest
from pydantic import BaseModel, Field
from typing import Optional
import uuid

router = APIRouter(prefix="/access", tags=["access-control"])


# ===== REQUEST/RESPONSE MODELS =====

class ValidateAccessRequest(BaseModel):
    test_id: str
    access_code: str


class StartAttemptRequest(BaseModel):
    test_id: str
    access_code: str


class CompleteAttemptRequest(BaseModel):
    attempt_id: str
    answers: dict
    time_taken_seconds: int


class RequestAttemptsRequest(BaseModel):
    test_id: str
    access_code: str
    requested_attempts: int = Field(ge=1, le=20)
    reason: Optional[str] = None


# ===== HELPER FUNCTIONS =====

def get_session_hash(request: Request) -> str:
    """Extract session hash from request."""
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return AccessCodeService.create_session_hash(ip, user_agent)


# ===== ACCESS CONTROL ENDPOINTS =====

@router.post("/validate")
async def validate_access_code(
    req: ValidateAccessRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Validate access code and check attempt limits."""
    try:
        test_id = uuid.UUID(req.test_id)
        session_hash = get_session_hash(request)
        
        is_valid, error_message = AccessCodeService.validate_access_code(
            db=db,
            test_id=test_id,
            access_code=req.access_code,
            session_hash=session_hash
        )
        
        if not is_valid:
            return {
                "valid": False,
                "error": error_message
            }
        
        # Get attempt summary
        summary = AccessCodeService.get_attempt_summary(db, test_id, session_hash)
        
        return {
            "valid": True,
            "test_id": str(test_id),
            "attempts_remaining": summary["attempts_remaining"],
            "best_score": summary["best_score"]
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-attempt")
async def start_exam_attempt(
    req: StartAttemptRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Start a new exam attempt."""
    try:
        test_id = uuid.UUID(req.test_id)
        session_hash = get_session_hash(request)
        
        attempt = AccessCodeService.start_exam_attempt(
            db=db,
            test_id=test_id,
            access_code=req.access_code,
            session_hash=session_hash
        )
        
        if not attempt:
            raise HTTPException(status_code=403, detail="Access denied or attempt limit reached")
        
        return {
            "attempt_id": str(attempt.id),
            "attempt_number": attempt.attempt_number,
            "answers": attempt.answers or {},
            "started_at": attempt.started_at.isoformat()
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete-attempt")
async def complete_exam_attempt(
    req: CompleteAttemptRequest,
    db: Session = Depends(get_db)
):
    """Complete an exam attempt with results."""
    raise HTTPException(status_code=410, detail="Submit to /tests/{test_id}/submit; client scores are not accepted")


@router.get("/attempt-summary/{test_id}")
async def get_attempt_summary(
    test_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get summary of all attempts for this session."""
    try:
        test_uuid = uuid.UUID(test_id)
        session_hash = get_session_hash(request)
        
        summary = AccessCodeService.get_attempt_summary(db, test_uuid, session_hash)
        
        return summary
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request-attempts")
async def request_additional_attempts(
    req: RequestAttemptsRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request additional attempts (requires admin approval)."""
    try:
        test_id = uuid.UUID(req.test_id)
        session_hash = get_session_hash(request)
        deps.authorize_test(db, test_id, req.access_code)
        
        attempt_request = AccessCodeService.request_additional_attempts(
            db=db,
            test_id=test_id,
            access_code=req.access_code,
            session_hash=session_hash,
            requested_attempts=req.requested_attempts,
            reason=req.reason
        )
        
        return {
            "request_id": str(attempt_request.id),
            "status": attempt_request.status,
            "current_attempts": attempt_request.current_attempts,
            "requested_attempts": attempt_request.requested_attempts,
            "message": "Request submitted for admin review"
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ADMIN ENDPOINTS =====

@router.get("/admin/pending-requests", dependencies=[Depends(deps.get_admin)])
async def get_pending_requests(
    db: Session = Depends(get_db)
):
    """Get all pending attempt requests (admin only)."""
    try:
        requests = db.query(AttemptRequest).filter(
            AttemptRequest.status == "pending"
        ).all()
        
        return {
            "pending_requests": [
                {
                    "request_id": str(r.id),
                    "test_id": str(r.test_id),
                    "access_code": r.access_code,
                    "current_attempts": r.current_attempts,
                    "requested_attempts": r.requested_attempts,
                    "reason": r.reason,
                    "created_at": r.created_at.isoformat()
                }
                for r in requests
            ]
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/approve-request/{request_id}", dependencies=[Depends(deps.get_admin)])
async def approve_attempt_request(
    request_id: str,
    admin_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Approve an attempt request (admin only)."""
    try:
        req_uuid = uuid.UUID(request_id)
        attempt_request = db.query(AttemptRequest).filter(AttemptRequest.id == req_uuid).first()
        
        if not attempt_request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Update request status
        attempt_request.status = "approved"
        attempt_request.admin_notes = admin_notes
        
        # Update test max_attempts
        test = db.query(Test).filter(Test.id == attempt_request.test_id).first()
        if test:
            test.max_attempts = attempt_request.requested_attempts
        
        db.commit()
        
        return {
            "success": True,
            "message": "Request approved",
            "new_max_attempts": attempt_request.requested_attempts
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
