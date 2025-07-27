"""FastAPI application entry point for TechStore SaaS."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.search import router as search_api_router
from app.web.main import router as web_router
from app.web.search import router as search_web_router

app = FastAPI(
    title="TechStore SaaS",
    description="Sistema de gestión para tiendas de tecnología",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Templates
templates = Jinja2Templates(directory="src/app/templates")


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "TechStore API is running"}


# API routes (JSON)
app.include_router(search_api_router, prefix="/api/v1")

# Web routes (HTMX)
app.include_router(web_router)
app.include_router(search_web_router, prefix="/htmx")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
