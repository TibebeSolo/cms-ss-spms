# implementation_plan.md — SS-SPMS (MVP v1)
EOTC Sunday School Students Profile Management System — Phase 2 (Architecture & Planning) — CONFIRMED

This plan implements the approved `requirements.md` and `domain_model.md` artifacts and the confirmed Phase 2 decisions:
- Web UI approach: **Django server-rendered UI** (Templates + HTMX)
- Ethiopian calendar conversion: **ethioqen**
- PDF generation: **ReportLab**
- Fonts:
  - English: CMG Sans, Palatino, Garamond
  - Amharic: PowerGeez Unicode 1, Nyala, Nokia Pure Headline
- Non-SS Christian ID: **{ChurchAbbrev}{YY}{RRRRR}** (auto-generated; used as username)
- Backups: **daily pg_dump** to local disk + external drive + NAS + cloud storage

---

## 1. Target Architecture
### 1.1 Style
**Modular Monolith** (bounded contexts as Django apps) + **Service Layer** pattern.
- Business rules live in `services/` modules.
- Views (templates) and any APIs call services.
- Avoid cross-app model writes except through services.

### 1.2 Django project layout
```
ss_spms/
  manage.py
  config/
    settings/
      base.py
      dev.py
      prod.py
    urls.py
    wsgi.py
    asgi.py
  apps/
    org/
    identity/
    people/
    sundayschool/
    melody/
    audit/
    imports/
    reports/
  templates/
  static/
  media/                   # local uploads on-prem
  scripts/                 # ops scripts (backups, maintenance)
  docker/
  .github/workflows/
```

### 1.3 Tech stack
- Python 3.12+
- Django 5.x
- PostgreSQL 16+
- Redis (optional now; useful later for caching/background jobs)
- pytest + pytest-django
- ruff + black + pre-commit
- ReportLab for PDFs
- ethioqen for Ethiopian date conversion

---

## 2. Data Model Implementation Notes
Implement models per `domain_model.md` (latest), grouped by app:
- `org`: Parish, SundaySchool, SocialLink
- `identity`: UserAccount (custom user), Role, Permission, RolePermission, UserRole, AuthEventLog
- `people`: Christian, ConfessionFather, RelationshipType, ContactPerson, StudentContactLink
- `sundayschool`: SSStudentProfile, StudentStatus, Grade, Section, ClassGroup,
  StudentRegistrationRequest, StudentProfileUpdateRequest, GradeSectionChangeRequest,
  AttendanceSession, AttendanceRecord, AttendanceApproval, AttendanceEditLog
- `melody`: MezemranMembership, MezemranChangeRequest
- `audit`: AuditLog
- `imports`: ImportRun, ImportRowError

### 2.1 Constraints & indexes (minimum)
- Unique:
  - SSStudentProfile.ssid
  - (joined_year_eth, ss_roll_number) per SundaySchool scope
  - AttendanceRecord unique (attendance_session_id, ss_student_profile_id)
  - Mezemran roll unique per (mezmur_entry_year_eth, mezemran_roll_number)
  - Only one ACTIVE MezemranMembership per student (enforced in service + DB constraint if supported)
  - Non-SS Christian ID unique, used as username
- Indexes:
  - Attendance sessions by session_date_greg
  - Attendance records by ss_student_profile_id
  - Student list filters: (grade_id, section_id, student_status_id)
  - Approval request states and timestamps

### 2.2 Ethiopian Date storage (confirmed)
Store Ethiopian date fields + derived Gregorian date:
- eth_year, eth_month, eth_day (ints)
- greg_date (DATE)

Conversion done using **ethioqen**:
- validate Ethiopian month/day, including month 13
- derive greg_date on save (service layer to guarantee consistency)

---

## 3. ID Generation (confirmed)
### 3.1 SSID (SS students; also username)
Format: `{SSAbbrev}{YY}{RRR}`
- YY: last 2 digits of SS joined Ethiopian year
- RRR: 3-digit zero-padded roll (auto-increment per joined year; resets yearly)

### 3.2 Mezemran ID
Format: `{SSAbbrev}MZ{YY}{RRR}`
- YY: last 2 digits of Mezmur entry Ethiopian year
- RRR: 3-digit zero-padded roll (auto-increment per mezmur entry year; resets yearly)

### 3.3 Non-SS Christian ID (confirmed)
Format: `{ChurchAbbrev}{YY}{RRRRR}`
- ChurchAbbrev comes from Parish configuration (add a Parish abbreviation field).
- YY: last 2 digits of Ethiopian year at the time of creation/registration
- RRRRR: 5-digit zero-padded roll (auto-increment per year; resets yearly)

This ID is used as username for non-SS Christians in MVP v1.

All ID generation must be done transactionally (SELECT MAX + 1 within a DB transaction, with appropriate locks).

---

## 4. Workflows (State Machines)
### 4.1 Student Registration
Draft (HR Expert) → HR Executive Approves → Executive Leader Approves → Active

### 4.2 Student Profile Updates
HR Expert creates update request → HR Executive approves → apply changes.
Student remains Active while pending.

### 4.3 Grade/Section Changes
Same approval chain as registration.
On final approval, update SSStudentProfile grade/section; keep request as history.

### 4.4 Attendance
- HR Expert/HR Executive records
- HR Expert submits → session locked for HR Expert; pending approval
- HR Executive approves with required comment
- HR Executive may edit after approval, must log reason in AttendanceEditLog + AuditLog

### 4.5 Mezemran Membership
- Melody Officer drafts select/terminate/reselect
- Melody Executive approves with required comment + timestamp
- Executive Leader final approves with required comment + timestamp
- Apply membership update and generate ID upon final approval

---

## 5. Permissions & RBAC (confirmed approach)
Custom fixed permissions + model permissions.
Minimum custom permission codes:
- manage_users
- manage_roles
- manage_permissions
- create_student
- edit_student
- submit_student_for_approval
- approve_student
- view_students
- export_student_profile_pdf
- create_attendance
- submit_attendance
- approve_attendance
- edit_attendance_after_submit
- generate_reports
- manage_mezemran_membership
- issue_mezemran_id
- view_mezemran_reports
- export_mezemran_list_pdf
- import_attendance_file

Authorization is enforced in both views and services.

---

## 6. UI Plan (confirmed: server-rendered)
### 6.1 Django Templates + HTMX
- Page-based UI with HTMX partial updates for:
  - student list filtering
  - attendance grid submission
  - approval queues
  - Mezemran membership actions

### 6.2 Graphs
- Use a lightweight chart library (e.g., Chart.js) for:
  - by status
  - by grade
  - by gender
  - by joined year

---

## 7. PDFs (confirmed: ReportLab)
### 7.1 Outputs
- Student profile summary PDF:
  - SS logo, datetime, signature placeholders, stamp area
  - include Mezemran ID if active
- Mezemran certificate/card PDF:
  - header/footer like student export + signature/stamp placeholders
- Attendance printable sheet PDF

### 7.2 Fonts
Bundle fonts inside the repo (or in docker image) and register them in ReportLab:
- English: CMG Sans, Palatino, Garamond
- Amharic: PowerGeez Unicode 1, Nyala, Nokia Pure Headline

Note: font licensing must be confirmed for redistribution; if any font cannot be bundled, use a freely licensed substitute.

---

## 8. Imports (manual Firebase export)
- Upload CSV/Excel via admin UI
- Create ImportRun
- Parse rows:
  - match by SSID
  - fallback by full name
  - ambiguous/no match → ImportRowError
- Write attendance sessions/records using service layer
- Store summary counts

---

## 9. Auditing & Logging
- Auth logs: login success/failure + lockouts
- AuditLog for all sensitive actions (student, approvals, attendance, imports, mezemran actions, exports)

---

## 10. DevOps (GitHub + Docker + CI/CD)
### 10.1 Docker (dev + prod)
- Dev compose: django + postgres
- Prod compose: gunicorn + nginx + postgres
- Local media storage for on-prem

### 10.2 CI/CD (GitHub Actions)
On PR:
- ruff
- black --check
- pytest
On merge:
- build docker image
- deploy via SSH (docker compose pull/up)

### 10.3 Backups (confirmed)
Daily `pg_dump`:
- save to local disk on server
- replicate to external USB/HDD/SSD
- replicate to NAS
- replicate to cloud storage

Provide a `scripts/backup.sh` and a `walkthrough.md` procedure.
