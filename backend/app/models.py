from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=True), primar_key=True, default=uuid.uuid4)
    provider = Column(String, index=True)
    course_name = Column(String)
    completion_date = Column(String) # String for v0, update to date with error handling in v1
    credits = Column(Numeric)