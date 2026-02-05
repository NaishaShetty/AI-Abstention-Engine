import math
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import FailureLog

# Controls how fast old events lose influence
TIME_DECAY_RATE = 0.0005

# Controls how much success reduces risk
RECOVERY_RATE = 0.6


def compute_risk_score(db: Session):
    logs = db.query(FailureLog).order_by(FailureLog.timestamp).all()
    now = datetime.utcnow()

    risk = 0.0

    for log in logs:
        delta_t = (now - log.timestamp).total_seconds()
        time_weight = math.exp(-TIME_DECAY_RATE * delta_t)

        if log.error == 1:
            # Failure increases risk
            risk += 1.0 * time_weight
        else:
            # Success reduces risk (recovery)
            risk -= RECOVERY_RATE * time_weight
        
        # ✅ FIX: Cap at 0.0 INSIDE the loop so success doesn't accumulate 
        # infinitely and 'bury' new failure signals.
        risk = max(risk, 0.0)

    return risk
