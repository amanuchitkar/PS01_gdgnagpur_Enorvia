import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import api, pages

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    title="Kindered - Mental Health Early Detection Agent",
    description="AI-powered emotional wellness support and early detection",
    version="1.0.0",
)

# Ensure reports directory exists
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(api.router)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Kindered"}
