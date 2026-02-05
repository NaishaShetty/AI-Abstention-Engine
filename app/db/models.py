from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime

from app.db.database import Base


class FailureLog(Base):
    __tablename__ = "failure_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    confidence = Column(Float, nullable=False)
    error = Column(Integer, nullable=False)

    risk_score = Column(Float, nullable=False)

    # ✅ REQUIRED for your system
    decision = Column(String, nullable=False)
