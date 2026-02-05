from fastapi import FastAPI
from app.api.routes import router

from app.db.database import engine, Base
from app.db import models

# Create database tables
Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Adaptive AI Abstention Engine")

# Enable CORS for frontend communication
# In production, replace ["*"] with specific origins (e.g. ["http://localhost:5173"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ✅ API PREFIX
app.include_router(router, prefix="/api")

# Serve frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")

@app.get("/")
def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
