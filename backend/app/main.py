
from fastapi import FastAPI
from app.api.upload import router as upload_router

app = FastAPI(
    title="Listora AI",
    description="AI-powered e-commerce listing image generation platform",
    version="0.2.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Listora AI",
        "status": "Backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(upload_router, prefix="/api/v1", tags=["Image Upload"])

