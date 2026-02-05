import torch
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.model import SimpleClassifier
from app.core.failure_memory import compute_risk_score
from app.core.abstention import abstain_decision
from app.db.database import SessionLocal
from app.db.models import FailureLog
from app.schemas.request_response import PredictRequest, PredictResponse

router = APIRouter()

# Load trained model
model = SimpleClassifier(input_dim=5)
model.eval()


# -----------------------------
# Database dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Prediction endpoint
# -----------------------------
@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest, db: Session = Depends(get_db)):
    # Convert input
    x = torch.tensor(req.features).float()

    # Inference
    if req.force_error:
        confidence = 0.20 # Force a low confidence
        prediction = 0
    else:
        confidence = model(x).item()
        prediction = int(confidence >= 0.5)

    # 1. Get current system risk (before this click)
    current_risk = compute_risk_score(db)

    # 2. Make decision based on current confidence and system state
    decision, reason = abstain_decision(confidence, current_risk)

    # 3. Simulated error signal
    if req.force_error:
        error = 1
    else:
        error = int(confidence < 0.45)

    # 4. Save the event
    new_log = FailureLog(
        confidence=confidence,
        error=error,
        risk_score=0.0, # Placeholder
        decision=decision
    )
    db.add(new_log)
    db.commit()

    # 5. RECOMPUTE RISK (Now includes the event we just saved)
    final_risk = compute_risk_score(db)
    new_log.risk_score = final_risk
    db.commit()

    return PredictResponse(
        prediction=prediction,
        confidence=confidence,
        decision=decision,
        reason=reason
    )


# -----------------------------
# 🩺 Health endpoint
# -----------------------------
@router.get("/health")
def system_health(db: Session = Depends(get_db)):
    logs = (
        db.query(FailureLog)
        .order_by(FailureLog.timestamp.desc())
        .limit(50)
        .all()
    )

    if not logs:
        return {
            "status": "cold_start",
            "risk": 0.0,
            "abstain_rate_50": 0.0,
            "review_rate_50": 0.0
        }

    total = len(logs)

    # Recompute decisions (DO NOT store them)
    abstains = 0
    reviews = 0

    for l in logs:
        d, _ = abstain_decision(l.confidence, l.risk_score)
        if d == "ABSTAIN":
            abstains += 1
        elif d == "REVIEW":
            reviews += 1

    current_risk = logs[0].risk_score

    if current_risk < 2.0:
        risk_state = "low"
    elif current_risk < 5.0:
        risk_state = "elevated"
    else:
        risk_state = "critical"

    return {
        "status": "healthy",
        "risk": round(current_risk, 3),
        "risk_state": risk_state,
        "abstain_rate_50": round(abstains / total, 3),
        "review_rate_50": round(reviews / total, 3)
    }
