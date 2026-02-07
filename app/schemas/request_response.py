from pydantic import BaseModel
from typing import List, Optional

class PredictRequest(BaseModel):
    features: List[float]
    force_error: Optional[bool] = False


class PredictResponse(BaseModel):
    prediction: int
    confidence: float
    decision: str
    reasons: List[str]
    suppressed_prediction: Optional[int] = None
    risk_score: float
    uncertainty_band: str

