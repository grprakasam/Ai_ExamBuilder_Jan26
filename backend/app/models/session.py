from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, TypeDecorator
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_class import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Custom UUID type that works with both SQLite and PostgreSQL
class UUID(TypeDecorator):
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, str):
                return uuid.UUID(value)
            return value

class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID, ForeignKey("test.id"))
    user_id = Column(UUID, ForeignKey("user.id"), nullable=True) # Optional for now
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    answers = Column(JSON) # User's answers: {"0": "A", "1": "C", ...}
    score = Column(Float)
    feedback = Column(JSON)
    
    test = relationship("Test")
