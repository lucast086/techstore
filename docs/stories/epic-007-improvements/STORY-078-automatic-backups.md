# STORY-078: Automatic Database Backups to Google Drive

**Status:** Draft
**Priority:** P3 (Low)
**Type:** Infrastructure
**Epic:** [EPIC-007](./EPIC-007-system-improvements.md)

## Story
As a system administrator, I need the database to automatically backup to Google Drive on a configurable schedule (daily/weekly) to ensure data safety and recovery capability.

## Business Value
- Protects against data loss
- Enables disaster recovery
- Provides historical snapshots
- Meets data retention requirements
- Peace of mind for business continuity

## Acceptance Criteria
- [ ] Configurable backup frequency (daily/weekly)
- [ ] Automatic execution based on schedule
- [ ] Backups uploaded to Google Drive
- [ ] Retention policy (keep last 30 backups)
- [ ] Email notification on backup failure
- [ ] Manual backup command available
- [ ] Backup logs viewable in admin panel
- [ ] Restore instructions documented

## Technical Implementation

### Files to Create/Modify
- `/src/app/services/backup_service.py` - Core backup logic
- `/src/app/tasks/backup_task.py` - Scheduled task
- `/src/app/config.py` - Backup configuration
- `/src/app/cli/commands.py` - Manual backup command
- `/src/app/web/admin.py` - Backup logs view
- `/src/app/templates/admin/backups.html` - UI for logs
- `/pyproject.toml` - Add dependencies
- `/.env.example` - Google Drive credentials

### Tasks
- [ ] Set up Google Drive API credentials
- [ ] Create backup service with PostgreSQL dump
- [ ] Implement Google Drive upload
- [ ] Create scheduled task runner
- [ ] Add retention policy logic
- [ ] Implement email notifications
- [ ] Create manual backup command
- [ ] Add admin panel for logs
- [ ] Write restore documentation
- [ ] Test backup and restore process

### Implementation Design
```python
# backup_service.py
import subprocess
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class BackupService:
    def __init__(self):
        self.drive_service = self._init_google_drive()

    def create_backup(self):
        # Generate backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"techstore_backup_{timestamp}.sql"

        # Create PostgreSQL dump
        subprocess.run([
            'pg_dump',
            settings.DATABASE_URL,
            '-f', f'/tmp/{filename}'
        ])

        # Compress backup
        subprocess.run([
            'gzip', f'/tmp/{filename}'
        ])

        # Upload to Google Drive
        self.upload_to_drive(f'/tmp/{filename}.gz')

        # Clean old backups
        self.enforce_retention_policy()

        # Log backup
        self.log_backup(filename)

        return filename

    def upload_to_drive(self, file_path):
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [settings.GDRIVE_BACKUP_FOLDER_ID]
        }

        media = MediaFileUpload(
            file_path,
            mimetype='application/gzip'
        )

        self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
```

```python
# Scheduled task using APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def schedule_backups():
    if settings.BACKUP_SCHEDULE == 'daily':
        scheduler.add_job(
            backup_service.create_backup,
            'cron',
            hour=3,  # 3 AM
            minute=0
        )
    elif settings.BACKUP_SCHEDULE == 'weekly':
        scheduler.add_job(
            backup_service.create_backup,
            'cron',
            day_of_week=0,  # Monday
            hour=3,
            minute=0
        )

    scheduler.start()
```

```bash
# CLI command
poetry run python -m app.cli backup-now
```

### Configuration
```python
# config.py
BACKUP_ENABLED = env.bool("BACKUP_ENABLED", False)
BACKUP_SCHEDULE = env.str("BACKUP_SCHEDULE", "daily")  # daily|weekly
BACKUP_RETENTION_DAYS = env.int("BACKUP_RETENTION_DAYS", 30)
GDRIVE_CREDENTIALS_PATH = env.str("GDRIVE_CREDENTIALS_PATH")
GDRIVE_BACKUP_FOLDER_ID = env.str("GDRIVE_BACKUP_FOLDER_ID")
BACKUP_NOTIFICATION_EMAIL = env.str("BACKUP_NOTIFICATION_EMAIL")
```

## Testing Requirements
- Test manual backup command
- Verify Google Drive upload
- Test retention policy (delete old backups)
- Simulate backup failure for notifications
- Test restore from backup
- Verify scheduling works
- Test with large database

## Security Considerations
- Encrypt backups before upload
- Secure Google Drive credentials
- Limit API permissions (write-only)
- Audit backup access
- Consider GDPR compliance

## Monitoring
- Daily backup success/failure logs
- Disk space monitoring
- Google Drive quota monitoring
- Alert on consecutive failures

## Dev Notes
- Consider incremental backups for large databases
- May need to use Google Cloud Storage for larger files
- Consider backup rotation strategy
- Document restore procedure clearly

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
