"""Job Database Model."""
import enum
from sqlalchemy import Column, Integer, String, Text
from app.database.base import Base

class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
