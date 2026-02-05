import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import FailureLog

WINDOW = 20  # rolling window size

def rolling_rate(values, window):
    rates = []
    for i in range(len(values)):
        start = max(0, i - window)
        window_vals = values[start:i + 1]
        rates.append(sum(window_vals) / len(window_vals))
    return rates


def main():
    db: Session = SessionLocal()

    logs = (
        db.query(FailureLog)
        .order_by(FailureLog.timestamp.asc())
        .all()
    )

    if not logs:
        print("No data to plot.")
        return

    risk_scores = [log.risk_score for log in logs]
    abstain_flags = [1 if log.decision == "ABSTAIN" else 0 for log in logs]
    review_flags = [1 if log.decision == "REVIEW" else 0 for log in logs]

    abstain_rate = rolling_rate(abstain_flags, WINDOW)
    review_rate = rolling_rate(review_flags, WINDOW)

    x = list(range(len(risk_scores)))

    plt.figure(figsize=(12, 6))

    # Risk curve
    plt.plot(x, risk_scores, label="Temporal Risk Score")

    # Threshold
    plt.axhline(
        y=3.0,
        linestyle="--",
        label="Abstention Threshold"
    )

    # Monitoring metrics
    plt.plot(x, abstain_rate, label="Rolling % ABSTAIN", alpha=0.8)
    plt.plot(x, review_rate, label="Rolling % REVIEW", alpha=0.8)

    plt.title("System Risk & Decision Rates Over Time")
    plt.xlabel("Request Index")
    plt.ylabel("Risk / Rate")
    plt.legend()
    plt.grid(True)

    plt.show()


if __name__ == "__main__":
    main()
