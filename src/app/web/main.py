"""Web routes for TechStore SaaS HTMX interface."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="src/app/templates")

# Variable para demo del contador
counter_value = 0
demo_products = [
    "iPhone 14 Pro",
    "Samsung Galaxy S23",
    "MacBook Pro M2",
    "iPad Air",
    "AirPods Pro",
    "Dell XPS 13",
    "Surface Pro 9",
    "Xiaomi Mi 13",
    "OnePlus 11",
    "Google Pixel 7",
]


@router.get("/", response_class=HTMLResponse)
async def welcome_page(request: Request):
    """Página de bienvenida con demos de HTMX."""
    return templates.TemplateResponse("welcome.html", {"request": request})


@router.post("/demo/increment")
async def increment_counter():
    """Demo HTMX: Incrementar contador."""
    global counter_value
    counter_value += 1
    return str(counter_value)


@router.post("/demo/decrement")
async def decrement_counter():
    """Demo HTMX: Decrementar contador."""
    global counter_value
    counter_value -= 1
    return str(counter_value)


@router.post("/demo/search")
async def search_demo(search_term: str = Form(...)):
    """Demo HTMX: Búsqueda en tiempo real."""
    if not search_term.strip():
        return "<p class='text-muted'>Escribe algo para buscar...</p>"

    # Filtrar productos que coincidan con el término de búsqueda
    results = [
        product for product in demo_products if search_term.lower() in product.lower()
    ]

    if not results:
        return "<p class='text-warning'>No se encontraron productos.</p>"

    html = ""
    for product in results:
        html += f"""
        <div class="result-item">
            <i class="fas fa-mobile-alt text-primary"></i> {product}
        </div>
        """

    return html


@router.get("/demo/status")
async def system_status():
    """Demo HTMX: Estado del sistema."""
    import random
    import time

    # Simular verificación de estado
    time.sleep(0.5)  # Simular delay de red

    statuses = [
        {
            "status": "online",
            "message": "Sistema funcionando correctamente",
            "icon": "fas fa-check-circle",
            "class": "text-success",
        },
        {
            "status": "warning",
            "message": "Algunas funciones en mantenimiento",
            "icon": "fas fa-exclamation-triangle",
            "class": "text-warning",
        },
        {
            "status": "error",
            "message": "Problemas de conectividad detectados",
            "icon": "fas fa-times-circle",
            "class": "text-danger",
        },
    ]

    current_status = random.choice(statuses)

    return f"""
    <div class="alert alert-{current_status['status']}" role="alert">
        <i class="{current_status['icon']} {current_status['class']}"></i>
        <strong>Estado:</strong> {current_status['message']}
        <br>
        <small class="text-muted">Última verificación: {time.strftime('%H:%M:%S')}</small>
    </div>
    <button
        class="btn btn-outline-primary btn-sm"
        hx-get="/demo/status"
        hx-target="#system-status"
        hx-swap="innerHTML">
        <i class="fas fa-refresh"></i> Verificar Nuevamente
    </button>
    """
