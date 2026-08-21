from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    provider = Column(String, index=True)
    course_name = Column(String)
    completion_date = Column(String) # String for v0, update to date with error handling in v1
    credits = Column(Numeric)