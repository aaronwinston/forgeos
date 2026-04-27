.PHONY: help dev seed backup restore

help:
@echo "ForgeOS Development Commands"
@echo "  make dev      - Start API and web servers"
@echo "  make seed     - Create default project and folders (personal mode only)"
@echo "  make backup   - Backup database and engine files"
@echo "  make restore  - Restore from backup"

dev:
@echo "Starting ForgeOS in personal mode..."
@echo "API: http://localhost:8000"
@echo "Web: http://localhost:3000"
@echo ""
cd apps/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$$!; \
sleep 2; \
cd apps/web && npm run dev &
WEB_PID=$$!; \
echo "Both servers running. Press Ctrl+C to stop."; \
wait

seed:
@echo "Seeding default project and folders..."
@cd apps/api && python3 << 'SEED_SCRIPT'
import os
import sys
sys.path.insert(0, '.')
from config import settings
from personal_mode import is_personal, PERSONAL_USER_ID, PERSONAL_ORG_ID
if not is_personal():
print("✗ Seeding only works in personal mode")
sys.exit(1)
from database import engine, create_db_and_tables
from models import Organization, Project, Folder, User, Membership
from sqlmodel import Session, select
create_db_and_tables()
with Session(engine) as session:
# Get personal org
org = session.exec(select(Organization).where(Organization.id == PERSONAL_ORG_ID)).first()
if not org:
print("✗ Personal org not found")
sys.exit(1)
# Get personal user
user = session.exec(select(User).where(User.user_id == PERSONAL_USER_ID)).first()
if not user:
print("✗ Personal user not found")
sys.exit(1)
# Check if default project exists
project = session.exec(
select(Project)
.where(Project.org_id == org.id)
.where(Project.name == "Arize")
).first()
if not project:
print("Creating default project: Arize")
project = Project(org_id=org.id, name="Arize", slug="arize")
session.add(project)
session.commit()
session.refresh(project)
# Create default folders
folders_to_create = ["In flight", "Ideas", "Archive"]
for folder_name in folders_to_create:
folder = session.exec(
select(Folder)
.where(Folder.project_id == project.id)
.where(Folder.name == folder_name)
).first()
if not folder:
print(f"Creating folder: {folder_name}")
folder = Folder(project_id=project.id, name=folder_name, slug=folder_name.lower().replace(" ", "-"))
session.add(folder)
session.commit()
print("✓ Seeding complete")
SEED_SCRIPT

backup:
@echo "Creating backup..."
@mkdir -p ~/forgeos-backups
@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
zip -r ~/forgeos-backups/forgeos_$$TIMESTAMP.zip \
apps/api/forgeos.db \
core/ context/ skills/ playbooks/ prompts/ rubrics/ briefs/ \
-q 2>/dev/null || true; \
echo "✓ Backup created: ~/forgeos-backups/forgeos_$$TIMESTAMP.zip"

restore:
@if [ -z "$(DATE)" ]; then \
echo "Usage: make restore DATE=YYYYMMDD_HHMMSS"; \
echo "Available backups:"; \
ls -1 ~/forgeos-backups/ 2>/dev/null | sed 's/forgeos_//;s/.zip//'; \
else \
echo "Restoring from backup: $(DATE)"; \
unzip -o ~/forgeos-backups/forgeos_$(DATE).zip -q; \
echo "✓ Restore complete"; \
fi
