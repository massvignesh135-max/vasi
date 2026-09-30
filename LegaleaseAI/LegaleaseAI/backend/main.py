from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from backend.routes import router
load_dotenv()

app = FastAPI(
    title="LegalEase AI",
    description="AI-powered legal document assistance API",
    version="1.0.0",
)

app.include_router(router)
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8501,http://127.0.0.1:8501"
)

origins = [
    origin.strip()
    for origin in cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to the LegalEase AI Legal Document Generator API.",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "LegalEase AI",
    }