import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router
from db.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# Create tables on startup (the app still runs if the database is unreachable)
init_db()

app = FastAPI(title="AlgoMentor — AI-Assisted Multi-Language Code Intelligence System")

# -------------------------------
# CORS (Frontend access)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# API routes
# -------------------------------
app.include_router(router, prefix="/api")

# -------------------------------
# Frontend: "/" → index.html, "/about.html" → about page
# (mounted last so it doesn't shadow /api)
# -------------------------------
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
