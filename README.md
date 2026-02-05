# AI-Abstention-Engine

# Real-time adaptive AI safety monitoring with self-recovery
A production-inspired system that demonstrates how AI models can know when not to answer, escalate uncertainty to humans, and dynamically recover from failures over time.

# Live Demo

- 📍 Dashboard (Local Demo): http://127.0.0.1:8000/
- 📍 Interactive API Docs (FastAPI / Swagger): http://127.0.0.1:8000/docs
  
Note: This project runs locally by design to showcase system behavior, not just static screenshots.

# What this project solves?

Modern AI systems shouldn’t blindly predict — they must:

- Detect low confidence
- Monitor historical reliability
- Escalate to human review
- Abstain safely under risk
- Recover automatically when conditions improve

The AI Abstention Engine implements all of this end-to-end.

# Core Features
# - Multi Stage Decision Engine
Every inference results in one of three decisions:

| Decision    | Meaning                                  |
| ----------- | ---------------------------------------- |
| **PROCEED** | Model confident & system healthy         |
| **REVIEW**  | Uncertain prediction → human oversight   |
| **ABSTAIN** | Unsafe to proceed → system blocks action |

Each decision includes a human-readable reason explaining why it was made.

# - Adaptive Risk Memory (The “Brain”)
- Tracks historical failures in a database
- Uses exponential time decay to reduce risk over time
- Supports self-recovery after instability
- Risk dynamically influences future decisions

This makes the system anti-fragile, not brittle.

# - Failure Injection (Safety Testing)
A built-in failure injection mechanism allows you to:

- Simulate low-confidence predictions
- Force risk spikes
- Observe real-time escalation to ABSTAIN
- Watch the system recover automatically

Perfect for demos and safety testing.

# - Real-Time Safety Dashboard
A simple  UI that visualizes:

- Live risk score
- System health state (LOW / ELEVATED / CRITICAL)
- Rolling ABSTAIN % and REVIEW %
- Risk evolution timeline

# Tech Stack:

# Backend (AI & API Core)

- Python 3.10+
- FastAPI – High-performance REST API
- PyTorch – Neural network inference (SimpleClassifier)
- SQLAlchemy – ORM for failure memory & logs
- SQLite – Lightweight persistent storage
- Pydantic – Robust request/response validation
- Uvicorn – ASGI server

# Frontend (Safety Dashboard)

- React – Dynamic single-page UI
- Tailwind CSS – Clean, professional, trust-focused design
- Chart.js – Real-time risk visualization
- Babel – On-the-fly JSX transpilation
- HTML5 / JavaScript (ES6+)

# Core Safety Systems

- Adaptive Risk Memory
- Exponential decay
- Recovery rates
- Multi-Stage Abstention Logic
- Confidence + historical risk
- Failure Injection Middleware
- Real-time safety simulation




