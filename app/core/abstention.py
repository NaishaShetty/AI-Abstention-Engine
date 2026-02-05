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
        reason (str): Human-readable explanation for traceability
    """

    # --- Hard safety gate: low confidence ---
    if confidence < LOW_CONF:
        return "ABSTAIN", "low_model_confidence"

    # --- Elevated risk: route to human review ---
    if risk >= ENTER_RISK_THRESHOLD:
        return "REVIEW", "elevated_system_risk"

    # --- Safe operating region ---
    if risk <= EXIT_RISK_THRESHOLD and confidence >= HIGH_CONF:
        return "PROCEED", "high_confidence_low_risk"

    # --- Default: uncertain regime ---
    return "REVIEW", "uncertain_confidence_risk_tradeoff"
