"""Job Validation Schemas."""
from pydantic import BaseModel
from typing import List, Optional

class JobBase(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
