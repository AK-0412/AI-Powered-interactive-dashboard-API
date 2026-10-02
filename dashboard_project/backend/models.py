from sqlalchemy import Column, Integer, String, Float
from database import Base

class MetricModel(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    name = Column(String)
    value = Column(Float)
    status = Column(String, default="Active")
    