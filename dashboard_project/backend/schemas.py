from pydantic import BaseModel
from typing import Optional

class MetricBase(BaseModel):
    category: str
    name: str
    value: float
    status: Optional[str] = "Active"

class MetricCreate(MetricBase):
    pass

class MetricResponse(MetricBase):
    id: int

    class Config:
        from_attributes = True
        