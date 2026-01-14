# Authentication & Access Flow - Exam Builder

## Overview

This document outlines the authentication and access control flow for the Exam Builder application. The system is designed to be **PII-minimal** (no email collection required) while maintaining secure access to exams.

---

## Core Principles

| Principle | Description |
|-----------|-------------|
| **No PII Collection** | No email or personal data required at exam entry |
| **Single Credential Set** | User keeps same TEST_ID + ACCESS_CODE for all attempts |
| **Admin Control** | Admin manages attempt limits and approvals |
| **Audit Trail** | System tracks all attempts per test |

---

## User Flow

### Phase 1: Test Creation

```
┌─────────────────────────────────────────────────────────────────┐
│  USER CREATES CUSTOMIZED TEST                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Select Subject                                          │
│  • Mathematics  • English  • Science  • Social Studies           │
│                                                                  │
│  Step 2: Configure Test                                          │
│  • Grade Level (3-12)                                            │
│  • Standard Focus (NCDPI/NEET/CBSE aligned)                      │
│  • Question Count (1-50)                                         │
│  • Question Type (MCQ / Open-Ended / Mixed)                      │
│  • Difficulty (Easy / Medium / Hard)                             │
│                                                                  │
│  Step 3: Generate Test                                           │
│  [AI generates questions based on configuration]                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 2: Access Credentials Generated

Upon successful test creation, the system automatically generates:

| Credential | Format | Example |
|------------|--------|---------|
| **TEST_ID** | UUID | `a1b2c3d4-5678-90ef-ghij-klmnopqrstuv` |
| **ACCESS_CODE** | 8-character alphanumeric | `X7K9M2PQ` |

```
┌─────────────────────────────────────────────────────────────────┐
│  🎉 TEST CREATED SUCCESSFULLY!                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📋 Your Test Credentials                                        │
│  ─────────────────────────────────────────                       │
│                                                                  │
│  TEST ID:      a1b2c3d4-5678-90ef-ghij-klmnopqrstuv             │
│  ACCESS CODE:  X7K9M2PQ                                          │
│                                                                  │
│  ⚠️  Save these credentials! You'll need them to start exam.    │
│                                                                  │
│  [📋 Copy to Clipboard]  [📥 Download PDF]  [📧 Share]           │
│                                                                  │
│  Options:                                                        │
│  • [Start Exam Now]                                              │
│  • [Take Later]                                                  │
│  • [Preview Questions]                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 3: Start Exam

User visits "Start Exam" page and enters credentials:

```
┌─────────────────────────────────────────────────────────────────┐
│  🔐 ENTER EXAM CREDENTIALS                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TEST ID:     [_________________________________]                │
│                                                                  │
│  ACCESS CODE: [________]                                         │
│                                                                  │
│  ℹ️  Attempts: 2 of 3 used                                       │
│                                                                  │
│                    [🚀 START EXAM]                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Validation Rules:**
- Wrong TEST_ID → "Test not found"
- Wrong ACCESS_CODE → "Invalid access code"
- Attempts exhausted → "No attempts remaining" (show request option)
- Code deactivated → "This exam is no longer available"

### Phase 4: Exam Mode

Standard exam interface with:
- Timer (auto-submit when time expires)
- Question navigation palette
- Mark for review functionality
- Practice mode (instant feedback) or Test mode (feedback at end)

### Phase 5: Results

- Score display
- Detailed feedback
- Performance analytics
- Option to download report

---

## Attempt Management System

### Default Behavior

| Setting | Default Value | Configurable By |
|---------|---------------|-----------------|
| Max Attempts per Test | 3 | Admin (global default) |
| Per-Test Override | N/A | Admin (per test) |

### When Attempts Are Exhausted

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  ATTEMPTS EXHAUSTED                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  You have used all 3 allowed attempts for this test.            │
│                                                                  │
│  Need more attempts?                                             │
│                                                                  │
│  Reason (optional): [________________________________]           │
│                                                                  │
│  [📨 REQUEST MORE ATTEMPTS]                                      │
│                                                                  │
│  Request will be sent to admin for approval.                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
User exhausts attempts
        │
        ▼
User clicks "Request More Attempts"
        │
        ▼
Optional: User provides reason
        │
        ▼
Request submitted to admin queue
        │
        ▼
Admin reviews request in dashboard
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
   [APPROVE]                           [DENY]
        │                                  │
        ▼                                  ▼
Admin selects +N attempts          Request closed
        │                           User notified
        ▼
max_attempts increased for that test
        │
        ▼
User can now continue with SAME TEST_ID + ACCESS_CODE
```

---

## Admin Dashboard

### Authentication Settings Page

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔐 Access Code Management                              [⚙️ Settings]   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ TEST ID          │ ACCESS   │ CREATED    │ USES  │ MAX │ STATUS   │ │
│  │                  │ CODE     │            │       │     │          │ │
│  ├──────────────────┼──────────┼────────────┼───────┼─────┼──────────┤ │
│  │ a1b2c3d4-5678... │ X7K9M2PQ │ 2026-01-14 │  0/3  │  3  │ 🟢 Active│ │
│  │ b2c3d4e5-6789... │ M3N8P2QR │ 2026-01-13 │  2/2  │  2  │ 🔴 Used  │ │
│  │ c3d4e5f6-7890... │ K9L2M5NP │ 2026-01-12 │  1/5  │  5  │ 🟢 Active│ │
│  │ d4e5f6g7-8901... │ P2Q5R8ST │ 2026-01-10 │  0/1  │  1  │ ⚫ Revoked│ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Actions per row:                                                       │
│  [👁️ View Test] [🔄 Regenerate Code] [❌ Revoke] [✏️ Edit Max Uses]     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Attempt Requests Queue

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📬 ATTEMPT REQUESTS (3 pending)                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ TEST ID: a1b2c3d4-5678...                                        │   │
│  │ Current: 3/3 attempts used                                       │   │
│  │ Requested: 2026-01-14 10:30 AM                                   │   │
│  │ Reason: "Need to retake after studying weak areas"               │   │
│  │                                                                  │   │
│  │ Add attempts: [+1] [+2] [+3] [+5] [Custom: ___]                  │   │
│  │                                                                  │   │
│  │ [✅ APPROVE]  [❌ DENY]                                           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Global Settings

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚙️ GLOBAL SETTINGS                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Default Max Attempts:        [3]                                       │
│  Access Code Length:          [8 characters]                            │
│  Code Expiration:             [30 days] / [Never]                       │
│  Rate Limit (failed attempts): [5 per hour per IP]                      │
│  Auto-approve requests after: [Disabled] / [X days]                     │
│                                                                         │
│  [💾 SAVE SETTINGS]                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Test Model (Modified)

```python
class Test(Base):
    # Existing fields...
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String)
    grade_level = Column(Integer)
    subject = Column(Enum(SubjectEnum))
    # ... other existing fields ...
    
    # NEW: Access Control Fields
    access_code = Column(String(10), unique=True, nullable=False)
    max_attempts = Column(Integer, default=3)
    current_attempts = Column(Integer, default=0)
    code_expires_at = Column(DateTime, nullable=True)
    is_code_active = Column(Boolean, default=True)
```

### AttemptRequest Model (New)

```python
class AttemptRequest(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID, ForeignKey("test.id"))
    reason = Column(Text, nullable=True)
    requested_at = Column(DateTime, server_default=func.now())
    status = Column(String, default="pending")  # pending, approved, denied
    additional_attempts_granted = Column(Integer, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID, ForeignKey("user.id"), nullable=True)
    
    test = relationship("Test", back_populates="attempt_requests")
```

### ExamAttempt Model (New - for tracking)

```python
class ExamAttempt(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID, ForeignKey("test.id"))
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    score = Column(Float, nullable=True)
    ip_address_hash = Column(String, nullable=True)  # Hashed for privacy
    
    test = relationship("Test", back_populates="attempts")
```

---

## API Endpoints

### Access Validation

```
POST /api/v1/exam/validate-access
Body: { "test_id": "uuid", "access_code": "string" }
Response: {
    "valid": true,
    "attempts_used": 2,
    "max_attempts": 3,
    "can_start": true
}
```

### Start Exam

```
POST /api/v1/exam/start
Body: { "test_id": "uuid", "access_code": "string" }
Response: {
    "attempt_id": "uuid",
    "test": { ... test data with questions ... }
}
```

### Request More Attempts

```
POST /api/v1/exam/request-attempts
Body: { "test_id": "uuid", "reason": "optional string" }
Response: {
    "request_id": "uuid",
    "status": "pending"
}
```

### Admin: Get Pending Requests

```
GET /api/v1/admin/attempt-requests?status=pending
Response: [
    {
        "id": "uuid",
        "test_id": "uuid",
        "reason": "string",
        "requested_at": "datetime",
        "current_attempts": 3,
        "max_attempts": 3
    }
]
```

### Admin: Resolve Request

```
POST /api/v1/admin/attempt-requests/{request_id}/resolve
Body: { "action": "approve", "additional_attempts": 2 }
Response: {
    "status": "approved",
    "new_max_attempts": 5
}
```

### Admin: Update Test Settings

```
PATCH /api/v1/admin/tests/{test_id}/access
Body: { 
    "max_attempts": 5,
    "is_code_active": true,
    "regenerate_code": false
}
```

---

## Security Considerations

| Security Measure | Implementation |
|------------------|----------------|
| **Rate Limiting** | Max 5 failed attempts per IP per hour |
| **Code Strength** | 8-character alphanumeric (62^8 = 218 trillion combinations) |
| **HTTPS Only** | All authentication over TLS |
| **IP Hashing** | Store hashed IP for audit, not raw IP |
| **Code Expiration** | Optional expiration after N days |
| **Brute Force Protection** | Exponential backoff on failed attempts |

---

## Summary

### Key Features

1. ✅ **No PII Collection** - No email required at exam entry
2. ✅ **Single Credential Set** - Same TEST_ID + ACCESS_CODE for all attempts
3. ✅ **Configurable Attempts** - Admin sets default, can override per-test
4. ✅ **In-App Request System** - Users request more attempts within app
5. ✅ **Admin Dashboard** - Monitor all tests, codes, and requests
6. ✅ **Audit Trail** - Track all attempts without storing PII

### User Journey Summary

```
CREATE TEST ──▶ GET CREDENTIALS ──▶ ENTER CODE ──▶ TAKE EXAM ──▶ VIEW RESULTS
                (TEST_ID +          (Validates      (N attempts    
                 ACCESS_CODE)        attempts)       allowed)
                                         │
                                         ▼
                              EXHAUSTED? ──▶ REQUEST MORE ──▶ ADMIN APPROVES
                                                                    │
                                                                    ▼
                                                          CONTINUE WITH
                                                          SAME CREDENTIALS
```

---

## Implementation Priority

1. **Phase 1**: Add access_code generation to test creation
2. **Phase 2**: Create "Start Exam" validation page
3. **Phase 3**: Implement attempt tracking
4. **Phase 4**: Build admin dashboard for code management
5. **Phase 5**: Add attempt request system
6. **Phase 6**: Security hardening (rate limiting, expiration)

---

*Document Version: 1.0*  
*Last Updated: January 14, 2026*
