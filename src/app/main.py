"""FastAPI application entry point for TechStore SaaS."""

import os
import sys

print("[STARTUP] main.py is being imported", file=sys.stderr)
print(f"[STARTUP] PORT env var: {os.environ.get('PORT', 'NOT SET')}", file=sys.stderr)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1 import auth as auth_api
from app.api.v1 import cash_closings as cash_closings_api
from app.api.v1 import customers as customers_api
from app.api.v1 import health as health_api
from app.api.v1 import payments as payments_api
from app.api.v1 import repairs as repairs_api
from app.api.v1 import sales as sales_api
from app.api.v1 import temp_setup  # TEMPORARY - DELETE AFTER USE
from app.api.v1 import warranties as warranties_api
from app.middleware.auth_context import AuthContextMiddleware
from app.web import (
    admin,
    auth,
    cash_closings,
    customers,
    payments,
    products,
    repairs,
    sales,
    warranties,
)
from app.web.main import router as web_router

app = FastAPI(
    title="TechStore SaaS",
    description="Sistema de gestión para tiendas de tecnología",
    version="0.1.0",
)

print("[STARTUP] FastAPI app created successfully", file=sys.stderr)

# Auth context middleware (must be added before CORS)
app.add_middleware(AuthContextMiddleware)

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


# Root redirect to login
@app.get("/")
async def root():
    """Redirect root to login page."""
    return RedirectResponse(url="/login", status_code=302)


# API routes
app.include_router(health_api.router, prefix="/api/v1")
app.include_router(auth_api.router)  # Auth API endpoints
app.include_router(customers_api.router, prefix="/api/v1")  # Customer API endpoints
app.include_router(payments_api.router, prefix="/api/v1")  # Payment API endpoints
app.include_router(
    sales_api.router, prefix="/api/v1/sales", tags=["sales"]
)  # Sales API endpoints
app.include_router(
    repairs_api.router, prefix="/api/v1/repairs", tags=["repairs"]
)  # Repair API endpoints
app.include_router(
    warranties_api.router, prefix="/api/v1", tags=["warranties"]
)  # Warranty API endpoints
app.include_router(
    cash_closings_api.router, prefix="/api/v1/cash-closings", tags=["cash-closings"]
)  # Cash Closing API endpoints
app.include_router(temp_setup.router, prefix="/api/v1")  # TEMPORARY - DELETE AFTER USE

# Auth routes (HTMX)
app.include_router(auth.router, tags=["auth"])

# Admin routes
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Customer routes (HTMX)
app.include_router(customers.router, tags=["customers"])

# Payment routes (HTMX)
app.include_router(payments.router, tags=["payments"])

# Product routes (HTMX)
app.include_router(products.router, tags=["products"])

# Sales routes (HTMX)
app.include_router(sales.router, prefix="/sales", tags=["sales"])

# Repair routes (HTMX)
app.include_router(repairs.router, prefix="/repairs", tags=["repairs"])

# Warranty routes (HTMX)
app.include_router(warranties.router, prefix="/warranties", tags=["warranties"])

# Cash Closing routes (HTMX)
app.include_router(
    cash_closings.router, prefix="/cash-closings", tags=["cash-closings"]
)

# Web routes (HTMX)
app.include_router(web_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
