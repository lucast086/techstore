# STORY-078: Manual Database Backup System (MVP)

**Status:** Ready for Development
**Priority:** P2 (Medium)
**Type:** Infrastructure
**Epic:** [EPIC-007](./EPIC-007-system-improvements.md)

## Story
As a system administrator, I need to manually generate and download database backups from the admin dashboard to ensure data safety and enable recovery when needed.

## Business Value
- Protects against data loss
- Enables disaster recovery
- Provides on-demand snapshots before major changes
- Simple implementation without external dependencies
- Works seamlessly on Railway platform
- Peace of mind for business continuity

## MVP Acceptance Criteria
- [ ] Manual backup generation from admin dashboard
- [ ] Download backup as `.sql.gz` file
- [ ] Admin-only access control
- [ ] Progress indicator during backup generation
- [ ] Clear restore instructions in documentation
- [ ] Works in production (Railway) environment
- [ ] Backup includes all tables and data
- [ ] Filename includes timestamp for identification

## Technical Implementation

### MVP Architecture
Simple on-demand backup system with direct download, no external storage dependencies.

### Files to Create/Modify
- `/src/app/services/backup_service.py` - Core backup logic
- `/src/app/api/v1/admin/backups.py` - Admin API endpoints
- `/src/app/web/admin/backups.py` - Web interface routes
- `/src/app/templates/admin/backups.html` - Admin UI
- `/src/app/dependencies.py` - Admin authentication check
- `/tests/test_services/test_backup_service.py` - Service tests
- `/docs/admin/backup-restore-guide.md` - Documentation

### MVP Tasks
- [ ] Create BackupService with pg_dump integration
- [ ] Implement backup compression with gzip
- [ ] Create API endpoint for backup generation
- [ ] Add download endpoint with streaming response
- [ ] Build admin dashboard interface
- [ ] Add admin-only access control
- [ ] Write comprehensive restore documentation
- [ ] Test backup/restore process in staging
- [ ] Verify Railway production compatibility

### MVP Implementation Design

```python
# services/backup_service.py
import subprocess
import gzip
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, BinaryIO
from sqlalchemy.orm import Session
from app.config import settings

class BackupService:
    def __init__(self, db: Session):
        self.db = db

    def create_backup(self) -> tuple[str, Path]:
        """Generate database backup and return filename and path"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"techstore_backup_{timestamp}.sql"

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as tmp_file:
            sql_path = Path(tmp_file.name)

        # Generate PostgreSQL dump
        result = subprocess.run([
            'pg_dump',
            settings.DATABASE_URL,
            '--no-owner',
            '--no-acl',
            '--if-exists',
            '--clean',
            '-f', str(sql_path)
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Backup failed: {result.stderr}")

        # Compress the backup
        gz_path = sql_path.with_suffix('.sql.gz')
        with open(sql_path, 'rb') as f_in:
            with gzip.open(gz_path, 'wb', compresslevel=9) as f_out:
                f_out.writelines(f_in)

        # Clean up uncompressed file
        sql_path.unlink()

        return f"{filename}.gz", gz_path

    def get_backup_stream(self, backup_path: Path) -> BinaryIO:
        """Return backup file as stream for download"""
        return open(backup_path, 'rb')
```

```python
# api/v1/admin/backups.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.services.backup_service import BackupService
from app.dependencies import get_admin_user

router = APIRouter(prefix="/admin/backups", tags=["admin"])

@router.post("/generate")
async def generate_backup(
    admin=Depends(get_admin_user),
    backup_service: BackupService = Depends()
):
    """Generate new database backup"""
    try:
        filename, path = backup_service.create_backup()
        return {
            "status": "success",
            "filename": filename,
            "download_url": f"/api/v1/admin/backups/download/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_backup(
    filename: str,
    admin=Depends(get_admin_user),
    backup_service: BackupService = Depends()
):
    """Download backup file"""
    # Security: validate filename format
    if not filename.match(r'^techstore_backup_\d{8}_\d{6}\.sql\.gz$'):
        raise HTTPException(status_code=400, detail="Invalid filename")

    backup_path = Path(f"/tmp/{filename}")
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup not found")

    return StreamingResponse(
        backup_service.get_backup_stream(backup_path),
        media_type="application/gzip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
```

```html
<!-- templates/admin/backups.html -->
{% extends "base.html" %}
{% block content %}
<div class="container mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6">Sistema de Backups</h1>

    <div class="bg-white rounded-lg shadow p-6">
        <button
            hx-post="/api/v1/admin/backups/generate"
            hx-indicator="#backup-spinner"
            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
            Generar Backup
        </button>

        <div id="backup-spinner" class="htmx-indicator">
            Generando backup...
        </div>

        <div id="backup-result" class="mt-4"></div>
    </div>

    <div class="mt-6 bg-gray-50 rounded-lg p-4">
        <h2 class="font-semibold mb-2">Instrucciones de Restauración:</h2>
        <pre class="text-sm">
1. Descargar el archivo .sql.gz
2. Descomprimir: gunzip backup.sql.gz
3. Restaurar: psql $DATABASE_URL < backup.sql
        </pre>
    </div>
</div>
{% endblock %}
```

### Configuration
```python
# No external configuration needed for MVP
# Uses existing DATABASE_URL from environment
```

## Testing Requirements
- Test backup generation with mock pg_dump
- Verify compression works correctly
- Test download endpoint with streaming
- Verify admin-only access control
- Test with different database sizes
- Validate restore process works
- Test error handling for failed backups
- Verify temporary file cleanup

## Security Considerations
- Admin-only access required
- Filename validation to prevent path traversal
- Temporary files cleaned up after download
- No sensitive data in logs
- Database credentials from environment only
- Consider adding backup encryption in future

## Production Considerations
- Railway compatible (uses pg_dump from system)
- Temporary storage in /tmp (cleared on deploy)
- Streaming download to handle large files
- No external dependencies (Google Drive, S3)
- Works with existing DATABASE_URL

## Future Enhancements (Phase 2)
- Scheduled automatic backups (daily/weekly)
- Upload to cloud storage (S3/Google Drive)
- Backup retention policy
- Email notifications on failure
- Incremental backups for large databases
- Backup history and management UI
- One-click restore from UI

---

## Dev Agent Record

### Task Progress
- [ ] Setup Google Drive API
- [ ] Create backup service
- [ ] Implement scheduling
- [ ] Add retention policy
- [ ] Create admin UI
- [ ] Test full cycle

### Debug Log

### Completion Notes

### File List

### Change Log

### Agent Model Used
