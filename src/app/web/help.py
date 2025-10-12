"""Help center and documentation routes."""

from pathlib import Path

import markdown
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.core.web_auth import get_current_user_optional
from app.models.user import User
from app.utils.templates import create_templates

templates = create_templates()

router = APIRouter(prefix="/ayuda", tags=["help"])

# Path to documentation files - relative to project root
DOCS_PATH = Path(__file__).parent.parent.parent.parent / "docs" / "user-guide" / "es"


@router.get("", response_class=HTMLResponse)
async def help_center(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
):
    """Display the main help center page."""
    return templates.TemplateResponse(
        "help/index.html",
        {
            "request": request,
            "title": "Centro de Ayuda",
            "current_user": current_user,
        },
    )


@router.get("/guia-rapida", response_class=HTMLResponse)
async def quick_guide(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
):
    """Display the quick start guide."""
    try:
        # Read the markdown file
        guide_path = DOCS_PATH / "GUIA-RAPIDA.md"
        with open(guide_path, encoding="utf-8") as f:
            content = f.read()

        # Convert markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=["extra", "codehilite", "tables", "toc"],
        )

        return templates.TemplateResponse(
            "help/document.html",
            {
                "request": request,
                "title": "Guía Rápida - 5 Minutos",
                "content": html_content,
                "back_link": "/ayuda",
                "current_user": current_user,
            },
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Guía no encontrada")


@router.get("/documento/{doc_name}", response_class=HTMLResponse)
async def help_document(
    request: Request,
    doc_name: str,
    current_user: User = Depends(get_current_user_optional),
):
    """Display a specific help document."""
    # Map friendly names to actual file names
    doc_mapping = {
        "introduccion": "01-introduccion.md",
        "primeros-pasos": "02-primeros-pasos.md",
        "clientes": "03-gestion-clientes.md",
        "productos": "04-gestion-productos.md",
        "ventas": "05-proceso-ventas.md",
        "reparaciones": "06-gestion-reparaciones.md",
        "caja": "07-control-caja.md",
        "garantias": "08-garantias.md",
        "reportes": "09-reportes.md",
        "configuracion": "10-configuracion.md",
        "faq": "11-preguntas-frecuentes.md",
        "glosario": "12-glosario.md",
    }

    # Get the actual filename
    filename = doc_mapping.get(doc_name)
    if not filename:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    try:
        # Read the markdown file
        doc_path = DOCS_PATH / filename
        with open(doc_path, encoding="utf-8") as f:
            content = f.read()

        # Convert markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=["extra", "codehilite", "tables", "toc"],
        )

        # Get title from filename
        title = filename.replace(".md", "").replace("-", " ").title()

        return templates.TemplateResponse(
            "help/document.html",
            {
                "request": request,
                "title": title,
                "content": html_content,
                "back_link": "/ayuda",
                "current_user": current_user,
            },
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
