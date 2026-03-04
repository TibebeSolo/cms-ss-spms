# task.md — SS-SPMS (MVP v1) — CONFIRMED
Master checklist (Artifact-Driven Development)

Rule: If it’s not in an artifact, it doesn’t exist.

## Phase 2 — Architecture & Planning (CONFIRMED)
- [x] Confirm UI approach: Django Templates + HTMX
- [x] Confirm Ethiopian calendar conversion library: ethioqen
- [x] Confirm PDF engine: ReportLab
- [x] Confirm fonts: English (CMG Sans, Palatino, Garamond) / Amharic (PowerGeez Unicode 1, Nyala, Nokia Pure Headline)
- [x] Confirm non‑SS Christian ID strategy: {ChurchAbbrev}{YY}{RRRRR} (username)
- [x] Confirm backups: daily pg_dump to local + external + NAS + cloud
- [ ] Approve `implementation_plan.md`
- [ ] Approve `task.md`

## Phase 3 — Scaffolding & Execution

### 1) Repo & Tooling Setup
- [ ] Create GitHub repo
- [ ] Add README.md (project overview + quickstart)
- [ ] Add `.editorconfig`
- [ ] Add `pyproject.toml` (Django, psycopg, ethioqen, reportlab, ruff, black, pytest, openpyxl, pillow)
- [ ] Setup pre-commit (ruff, black, whitespace)
- [ ] Setup pytest + pytest-django
- [ ] Create `.env.example`

### 2) Dockerization (Dev + Prod)
- [ ] Create `docker-compose.dev.yml` (web + postgres)
- [ ] Create `docker-compose.prod.yml` (web/gunicorn + nginx + postgres)
- [ ] Create `Dockerfile` for Django app
- [ ] Create nginx config for static/media proxy
- [ ] Verify: `docker compose up` works; migrations run

### 3) CI/CD (GitHub Actions)
- [ ] Workflow on PR: ruff + black --check + pytest
- [ ] Workflow on merge: build & push docker image
- [ ] Workflow on merge: deploy via SSH (document required secrets)

### 4) Django Project Scaffolding
- [ ] Create Django project (`config/`) and apps (`apps/`)
- [ ] Settings split: base/dev/prod
- [ ] Configure Postgres + env vars
- [ ] Configure static + media (local for on-prem)
- [ ] Configure language toggle (Amharic default; English supported)

### 5) Identity & RBAC
- [ ] Implement custom user model (username/password)
- [ ] Implement Role/Permission models + assignments
- [ ] Seed default roles and permissions (MVP defaults)
- [ ] Implement auth logs + lockout after 7 failures
- [ ] System Admin UI for users/roles/permissions

### 6) Org Module
- [ ] Parish model (name/address/phone/diocese + church_abbrev field needed for non‑SS ID)
- [ ] SundaySchool model (name/abbrev/phone/logo/social links)
- [ ] Setup flow (create initial parish + SS profile)

### 7) People Module
- [ ] Christian model (partial allowed for non-students)
- [ ] ConfessionFather lightweight model
- [ ] RelationshipType customizable list
- [ ] ContactPerson + StudentContactLink (>=1 required for students)

### 8) SS Student Profiles
- [ ] Grade + Section models (customizable defaults)
- [ ] SSStudentProfile model (1:1 with Christian)
- [ ] SSID generation service: {SSAbbrev}{YY}{RRR} (3-digit roll)
- [ ] Non-SS Christian ID generation: {ChurchAbbrev}{YY}{RRRRR} (5-digit roll), username
- [ ] Registration workflow models + transitions
- [ ] Profile update workflow + transitions
- [ ] Grade/Section change workflow + transitions
- [ ] Student list/search/filter UI

### 9) Attendance
- [ ] ClassGroup (grade+section + meeting day)
- [ ] AttendanceSession/Record/Approval/EditLog
- [ ] Auto-create sessions by meeting day + manual session creation
- [ ] Entry UI (grid/table), submit/approve/edit with required comments

### 10) Imports
- [ ] ImportRun + ImportRowError
- [ ] CSV + Excel parsing (openpyxl)
- [ ] Matching by SSID + name fallback
- [ ] Admin UI upload + error review

### 11) Melody (Mezemran)
- [ ] MezemranMembership (history; only one active)
- [ ] Mezemran ID generation: {SSAbbrev}MZ{YY}{RRR} (3-digit roll)
- [ ] MezemranChangeRequest workflow: Officer → Dept Exec → Leader
- [ ] Reports + exports for Mezemran

### 12) Reports & Exports
- [ ] Required reports + graphs (Chart.js)
- [ ] Excel exports (openpyxl)
- [ ] PDF exports (ReportLab) with bundled fonts

### 13) Auditing
- [ ] AuditLog model + helper
- [ ] Wire audit into workflows + edits + imports + exports

### 14) Backups & Ops
- [ ] `scripts/backup.sh` using pg_dump
- [ ] Daily schedule documentation (cron/systemd timer)
- [ ] Copy backups to external + NAS + cloud (procedure)

### 15) Testing
- [ ] ID generation tests
- [ ] Workflow transition tests
- [ ] Import tests
- [ ] PDF smoke tests (font embedding)

### 16) Documentation
- [ ] `walkthrough.md` (dev, prod, backup, restore)
- [ ] `backlog.md` (finance, academic system, departments, Flutter API migration)
