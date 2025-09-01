#!/usr/bin/env python3
"""
Script para demostrar el flujo de carga de variables de entorno.
Muestra exactamente de dónde vienen las configuraciones.
"""

import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("🔍 DEBUG: Flujo de Carga de Variables de Entorno")
print("=" * 60)

# 1. Mostrar variables de entorno del sistema
print("\n1️⃣  Variables de Entorno del Sistema:")
print("-" * 40)
db_from_env = os.getenv("DATABASE_URL")
env_from_env = os.getenv("ENVIRONMENT")
print(f"DATABASE_URL en os.environ: {db_from_env if db_from_env else '❌ No existe'}")
print(f"ENVIRONMENT en os.environ: {env_from_env if env_from_env else '❌ No existe'}")

# 2. Mostrar contenido del archivo .env
print("\n2️⃣  Archivo .env:")
print("-" * 40)
env_file = Path(".env")
if env_file.exists():
    print("✅ Archivo .env existe")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "DATABASE_URL" in line:
                    # Ocultar credenciales
                    parts = line.split("@")
                    if len(parts) > 1:
                        print(f"   {parts[0].split('=')[0]}=***@{parts[1]}")
                    else:
                        print(f"   {line}")
                else:
                    print(f"   {line}")
else:
    print("❌ No existe archivo .env")

# 3. Cargar configuración con Pydantic
print("\n3️⃣  Configuración Cargada por Pydantic:")
print("-" * 40)

from app.config import Settings

# Crear nueva instancia para ver de dónde viene cada valor
settings = Settings()

# Mostrar valores finales
db_url = settings.DATABASE_URL
if "@" in db_url:
    # Ocultar credenciales
    parts = db_url.split("@")
    protocol = parts[0].split("://")[0]
    rest = parts[1] if len(parts) > 1 else ""
    display_url = f"{protocol}://***@{rest}"
else:
    display_url = db_url

print(f"DATABASE_URL final: {display_url}")
print(f"ENVIRONMENT final: {settings.environment}")

# 4. Determinar origen
print("\n4️⃣  Origen de la Configuración:")
print("-" * 40)

if db_from_env:
    print("✅ DATABASE_URL viene de: Variable de Entorno del Sistema")
    print("   (Como en Railway - máxima prioridad)")
elif env_file.exists() and "DATABASE_URL" in env_file.read_text():
    print("✅ DATABASE_URL viene de: Archivo .env")
    print("   (Desarrollo local - segunda prioridad)")
else:
    print("✅ DATABASE_URL viene de: Valor por defecto en config.py")
    print("   (Fallback - última prioridad)")

# 5. Mostrar conexión real
print("\n5️⃣  Conexión a Base de Datos:")
print("-" * 40)

from app.database import check_db_connection, engine

print(f"SQLAlchemy Engine URL: {display_url}")
print(f"Pool size: {engine.pool.size()}")
print(f"Echo SQL: {engine.echo}")

# Probar conexión
print("\n6️⃣  Test de Conexión:")
print("-" * 40)
if check_db_connection():
    print("✅ Conexión exitosa a la base de datos")

    from app.database import get_db_version

    version = get_db_version()
    if version:
        print(f"   PostgreSQL: {version.split(',')[0]}")

    # Contar tablas
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """
            )
        )
        table_count = result.scalar()
        print(f"   Tablas en la BD: {table_count}")

        result = conn.execute(text("SELECT current_database()"))
        db_name = result.scalar()
        print(f"   Nombre de la BD: {db_name}")
else:
    print("❌ No se pudo conectar a la base de datos")

print("\n" + "=" * 60)
print("📝 Resumen del Flujo:")
print("=" * 60)
print(
    """
1. Pydantic Settings busca DATABASE_URL en:
   - Primero: Variables de entorno del sistema (Railway)
   - Segundo: Archivo .env (Local)
   - Tercero: Valor default en config.py

2. SQLAlchemy usa ese DATABASE_URL para conectarse

3. Todas las queries pasan por esa conexión
"""
)

# Mostrar cuál ambiente está activo
if settings.environment == "production":
    print("⚠️  MODO PRODUCCIÓN - Ten cuidado con las operaciones")
else:
    print("✅ MODO DESARROLLO - Seguro para pruebas")
