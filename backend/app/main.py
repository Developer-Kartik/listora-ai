from fastapi import FastAPI

app = FastAPI(
    title="Listora AI",
    description="AI-powered e-commerce listing image generation platform",
    version="0.1.0"
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
