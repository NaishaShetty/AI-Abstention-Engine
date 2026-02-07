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
import os
MODEL_PATH = os.path.join(os.getcwd(), "model.pt")
model = SimpleClassifier(input_dim=5)
if os.path.exists(MODEL_PATH):
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
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

    # Model Inference
    if req.force_error:
        confidence = 0.20 # Force a low confidence
    else:
        with torch.no_grad():
            confidence = model(x).item()
    
    raw_prediction = int(confidence >= 0.5)

    # 1. Get current system risk
    current_risk = compute_risk_score(db)

    # 2. Make decision based on current confidence and system state
    decision, reasons, band = abstain_decision(confidence, current_risk)

    # 3. Suppressed/Actual Prediction
    # If ABSTAIN, prediction is -1 (null), but we show what it would have been
    if decision == "ABSTAIN":
        final_prediction = -1 
        suppressed = raw_prediction
    else:
        final_prediction = raw_prediction
        suppressed = None

    # 4. Simulated error signal for risk engine
    error = int(confidence < 0.45) if not req.force_error else 1

    # 5. Save the event
    new_log = FailureLog(
        confidence=confidence,
        error=error,
        risk_score=current_risk, # Store risk at time of decision
        decision=decision
    )
    db.add(new_log)
    db.commit()

    # 6. Update shared risk (simplified: compute after save)
    final_risk = compute_risk_score(db)
    new_log.risk_score = final_risk # Corrected to final risk after event
    db.commit()

    return PredictResponse(
        prediction=final_prediction,
        confidence=confidence,
        decision=decision,
        reasons=reasons,
        suppressed_prediction=suppressed,
        risk_score=final_risk,
        uncertainty_band=band
    )


# -----------------------------
# 🩺 Health endpoint
# -----------------------------
@router.get("/health")
def system_health(db: Session = Depends(get_db)):
    from app.core.failure_memory import TIME_DECAY_RATE
    from app.core.abstention import EXIT_RISK_THRESHOLD
    import math

    log = db.query(FailureLog).order_by(FailureLog.timestamp.desc()).first()
    
    if not log:
        return {"status": "cold_start", "risk": 0.0, "risk_state": "low"}

    current_risk = compute_risk_score(db)
    
    # Recovery ETA Calculation
    if current_risk > EXIT_RISK_THRESHOLD:
        eta_seconds = -math.log(EXIT_RISK_THRESHOLD / current_risk) / TIME_DECAY_RATE
    else:
        eta_seconds = 0


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
        "recovery_eta_seconds": round(max(eta_seconds, 0), 1)
    }

# -----------------------------
# 📊 Metrics endpoint
# -----------------------------
@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    logs = db.query(FailureLog).order_by(FailureLog.timestamp.desc()).limit(100).all()
    
    if not logs:
        return {"msg": "no data"}

    total = len(logs)
    abstains = sum(1 for l in logs if l.decision == "ABSTAIN")
    reviews = sum(1 for l in logs if l.decision == "REVIEW")
    errors = sum(1 for l in logs if l.error == 1)
    avg_conf = sum(l.confidence for l in logs) / total

    return {
        "avg_confidence": round(avg_conf, 3),
        "abstain_rate": round(abstains / total, 3),
        "review_rate": round(reviews / total, 3),
        "error_rate": round(errors / total, 3),
        "total_events": total,
        # Audit Log for table
        "audit_log": [{
            "timestamp": l.timestamp.strftime("%H:%M:%S"),
            "confidence": round(l.confidence, 3),
            "decision": l.decision,
            "risk": round(l.risk_score, 2),
            "error": l.error
        } for l in logs[:10]]
    }

