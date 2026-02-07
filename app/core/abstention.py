# Confidence thresholds
LOW_CONF = 0.45          # Below this → ABSTAIN
HIGH_CONF = 0.85         # Above this (with low risk) → PROCEED

# Risk thresholds (hysteresis band)
ENTER_RISK_THRESHOLD = 3.0   # Enter risky regime
EXIT_RISK_THRESHOLD = 1.5    # Exit risky regime (lower to avoid flapping)

# =========================
# Decision Function
# =========================

def abstain_decision(confidence: float, risk: float):
    """
    Decide whether the system should PROCEED, REVIEW, or ABSTAIN.

    Returns:
        decision (str): One of ["PROCEED", "REVIEW", "ABSTAIN"]
        reasons (list): List of factors for traceability
        band (str): Uncertainty band label
    """
    reasons = []
    
    # 1. Determine Uncertainty Band
    if confidence < LOW_CONF:
        band = "unsafe"
        reasons.append("confidence_below_safety_threshold")
    elif confidence < HIGH_CONF:
        band = "uncertain"
        reasons.append("uncertainty_band_detection")
    else:
        band = "safe"

    # 2. Risk Factors
    if risk >= ENTER_RISK_THRESHOLD:
        reasons.append("high_system_risk_memory")
    elif risk > EXIT_RISK_THRESHOLD:
        reasons.append("system_in_recovery_mode")

    # 3. Final Decision Logic
    if confidence < LOW_CONF:
        return "ABSTAIN", reasons, band
    
    if risk >= ENTER_RISK_THRESHOLD:
        return "ABSTAIN", reasons, band # Tighten safety: Abstain mirror if risk is too high
    
    if risk > EXIT_RISK_THRESHOLD:
        return "REVIEW", reasons, band
        
    if confidence < HIGH_CONF:
        return "REVIEW", reasons, band

    return "PROCEED", ["optimal_operating_conditions"], band

