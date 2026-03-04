# Sunday School Students Profile Management System (SS-SPMS)
Ethiopian Orthodox Tewahedo Church (EOTC) — Single Parish Installation (MVP v1)

## 1. Purpose
Build an MVP system to manage Sunday School student (member) profiles for the Sunday School Human Resource Management Department, under one parish. The system is designed to grow later into additional Sunday School modules (finance, academic system, etc.) and ultimately a broader Church Management System (CMS).

## 2. MVP v1 Scope (Included)
MVP v1 includes:
1) Student (Sunday School member) profile management
2) Attendance tracking + attendance reports
3) Grade/Section grouping (minimal academic structure for grouping and attendance)
4) Role + permission customization (custom roles, fixed permission set)
5) Manual import/sync of attendance from existing Flutter/Firebase attendance export (CSV/Excel; one-way)
6) Melody Department (መዝሙር) basics: መዘምራን membership management (select/terminate/reselect + ID + approvals + reports + exports)

MVP v1 supports managing other parish members as “Christians” (canonical person records), not only SS students, to support:
- Confession father linking (reusable)
- Contact/emergency contact linking

## 3. Out of Scope (Explicitly NOT in MVP v1)
- Sunday School finance (monthly membership payment fee management)
- Full Sunday School academic system (teachers, grading, curriculum, performance)
- Other departments/ministry assignment (Academic dept, Arts dept, Finance, Inventory, etc.) — later versions
- Flutter app switching to Django API as backend (for MVP: Flutter stays on Firebase; manual import only)
- Multi-parish / diocese aggregation

## 4. Timeline (User-defined)
Target: 1 week for MVP v1.

## 5. Organization Setup (Parish + Sunday School)
### 5.1 Parish Profile (Required)
- parish name
- parish address
- parish phone
- diocese name

### 5.2 Sunday School Profile (Required)
Sunday School is a sub-organ of the parish:
- Sunday School name
- Sunday School abbreviation (used in SSID generation and Mezemran ID generation)
- Sunday School phone
- Sunday School logo
- Sunday School social media links

Constraint: One parish has exactly one Sunday School in MVP v1.

## 6. Users, Roles, Permissions, Authentication
### 6.1 Authentication
- Username/password login
- Password policy: minimum length 6 characters
- Password reset: only via System Admin (no self-service reset in MVP)
- Log authentication events: login success/failure
- Account lockout after 7 failed login attempts

### 6.2 Roles (Default Roles for MVP v1)
Roles are customizable by System Admin; the system must ship with these defaults:
- System Admin
- Sunday School Executives Leader
- Sunday School HR Department Executive Officer
- Sunday School HR Department Expert
- Melody Department Executive
- Melody Department Officer

### 6.3 Role Capabilities (MVP defaults)
- System Admin:
  - manage system configuration
  - manage users
  - manage roles
  - manage permissions
  - full access to all data
- Sunday School HR Department Expert:
  - register new student (create draft)
  - propose edits to student profile (creates pending update)
  - record attendance
  - submit attendance for approval
  - view student list
- Sunday School HR Department Executive Officer:
  - approve student registration steps (HR approval)
  - approve student profile updates
  - record attendance
  - edit attendance after submission/approval (requires reason note)
  - approve attendance
  - view student list
  - generate HR reports
- Sunday School Executives Leader:
  - final approval for student registration
  - final approval for student transfers to other churches’ SS
  - final approval for Mezemran membership actions (see §15)
  - view lists
  - generate reports
- Melody Department Officer:
  - draft Mezemran membership actions (select/terminate/reselect)
  - view Mezemran lists/reports
- Melody Department Executive:
  - approve Mezemran membership actions (department approval)
  - view Mezemran lists/reports
  - generate/export Mezemran reports

### 6.4 Custom Roles & Permissions
- System Admin can create custom roles at any time
- Permission set is fixed (enumerated) and assignable to roles
- Model-level permissions also apply (standard add/change/view patterns in addition to custom actions)
- In MVP v1, only System Admin manages users/roles/permissions

## 7. Core Data Concepts
### 7.1 Christian (Canonical Person)
A canonical person entity is called “Christian”.
- Christians may represent SS students, confession fathers, parents/contacts, and other parish members.
- A Christian may exist without being an SS student.

### 7.2 SS Student Profile (Sunday School student-specific)
SS student-specific fields must live in a separate profile linked to a Christian.

SS student-specific rules:
- SSID is the unique SS identifier and is used as the username for SS students.
- SSID format: `{SSAbbrev}{YY}{RRR}`
  - `YY` = last 2 digits of SS joined year (Ethiopian year)
  - `RRR` = 3-digit zero-padded roll number
  Example (SSAbbrev=ABSS, joined year 2011 EC): `ABSS11001`
- Roll number is system auto-increment, unique per joined year (roll resets each year).
- Joined year is Ethiopian calendar year.
- Student belongs to exactly one Grade+Section at a time.

### 7.3 Required Fields vs Partial Records
- Student profiles (SSStudentProfile) must be fully complete at creation (strict validation).
- Non-student Christians may be stored as partial records (draft/incomplete allowed).
- Baptismal name is mandatory for SS students.

## 8. Student Profile Fields (MVP v1)
### 8.1 SS Student Profile Required Fields (Must exist to register an SS student)
**Identity & Personal**
- Full name: first name, father name, grandfather name
- Mother’s name
- Sex
- Date of Birth (mandatory)
- Age (calculated, Ethiopian calendar age)
- Baptismal name (mandatory)
- Place of baptism (church)

**Contact**
- Phone number (unique per student)
- Email (unique per student)
- Residential Address:
  - Region
  - Town/City
  - Kebele
  - Home number

**Sunday School**
- Sunday School ID (SSID; system-generated; unique; also username)
- Sunday School joined year (Ethiopian year)
- Grade
- Section

**Other Required Attributes (MVP v1)**
- Marital Status (Single/Married)
- Special Talent
- Church Academic Level:
  - SS Preparatory KG
  - SS 1–12
  - Theology Diploma
  - Theology Degree/MSc
  - Kine
  - Zema
  - Metsahift Trguame
- Government Curriculum Academic Level:
  - Elementary
  - High school
  - Diploma
  - Degree
  - Masters
  - PhD
  - Professor
- Occupation (Job)
- Priesthood (Deacon/Priest)

**Confession Father Link**
- Confession father must be selectable as a reusable record (see §9)

**Photo**
- Passport-size photo upload required (no documents in MVP v1)

### 8.2 Confession Father Requirements (MVP v1)
Confession father is a lightweight entity:
- full name
- phone number
- servant church
- residence

A confession father record can be linked to many students.

### 8.3 Contact / Guardian (Emergency Contact)
At least one contact per student is required; additional contacts optional.
Contact fields:
- full name
- relationship type (customizable list)
- phone number
- address

Contacts can be shared across multiple students (e.g., siblings).
A contact may optionally reference an existing Christian record.

## 9. Grade/Section Grouping (MVP v1)
- Grades: KG, 1–12, plus System Admin can add custom grades
- Sections: customizable; default examples A/B/C
- Students belong to exactly one Grade+Section at a time
- Grade/Section changes are treated as transfers and require approval flow
- Grade/Section change history must store:
  - datetime
  - student reference
  - from grade/section
  - to grade/section
  - reason
  - drafted by
  - HR-approved by + timestamp + required comment
  - leader-approved by + timestamp + required comment

## 10. Approval Workflows (MVP v1)
### 10.1 Student Registration Workflow (Required)
Status flow:
Draft (HR Expert) → HR Executive Officer Approves → Executive Leader Approves → Active

Rules:
- On final approval (Active), system allows printing/exporting the student profile summary.

### 10.2 Student Profile Update Workflow (Required)
- When HR Expert edits a student profile, it enters “Pending Update Approval”
- Student remains Active while pending approval
- HR Executive Officer approval is required for profile updates
- All updates and approvals must be logged

### 10.3 Transfer Workflow (Grade/Section and “other church” transfer)
- Grade/Section change uses the same approval chain as registration.
- Transfer to other church SS uses the same approval chain as registration.
- For “other church” transfer in MVP: generate an exportable profile summary with approval signature placeholders (manual signing).

## 11. Student Statuses (MVP v1)
Student status is a single-choice value (one status at a time).
Default statuses:
- Active
- Transferred
- Not Complete
- Undetermined
- Elders

Statuses must be customizable by System Admin (add/edit), but defaults above must exist in MVP v1.
Status is manually set by HR (not system-calculated in MVP v1).

## 12. Attendance (MVP v1)
### 12.1 Attendance Scope
Primary attendance grouping: Grade+Section.
System also supports attendance for:
- whole Sunday School sessions
- special congregations/events

### 12.2 Sessions
- Auto-create sessions supported, and manual session creation supported.
- Meeting day is configurable (not always Sunday).
- Different grade/sections can have different meeting days.

### 12.3 Attendance Statuses
Fixed list for MVP v1:
- Present
- Absent
- Late
- Excused

### 12.4 Attendance Workflow & Permissions
- HR Expert and HR Executive Officer can record attendance.
- HR Expert can enter attendance initially, but cannot edit after “Submit”.
- “Submit” locks attendance for HR Expert and sets state to pending approval.
- HR Executive Officer approves attendance after submit.
- Approval must store: approver + timestamp + required comment.
- HR Executive Officer can edit attendance even after approval, but must provide a reason/note.
- All attendance actions (create/edit/submit/approve) must be audit logged.

### 12.5 Printable Attendance
System must generate printable attendance sheets and export attendance data.

## 13. Reports & Exports (MVP v1)
### 13.1 Reports Required
- Roster per class (grade/section) with filters: grade, section, status
- Attendance rate per student
- Weekly summary (whole Sunday School)
- Absentee list (default threshold: absent this session only; threshold configurable later)
- Total students list with limited attributes:
  - SSID
  - Full name
  - Baptismal name
  - Sex
  - Phone
  - Grade
  - Entry year
- Status analysis graphs (default breakdowns):
  - by status
  - by grade
  - by gender
  - by joined year

### 13.2 Export Formats
- Excel
- PDF

### 13.3 Student Profile Export (Required)
For any student (especially transfers), system must produce a printable/exportable profile summary suitable for hardcopy archiving and sharing with destination church.
PDF must include:
- Sunday School logo
- approval signature placeholders
- stamp area
- datetime

If the student is a Mezemran (active), the student profile export must also include Mezemran ID.

## 14. Firebase Attendance Import (MVP v1)
- Existing Flutter attendance app remains on Firebase in MVP v1.
- One-way manual import from Firebase export file(s) into this system.
- Supported import formats: CSV and Excel
- Import columns include:
  - SSID
  - date
  - status
  - grade/section
  - event type (regular vs special)
- Matching support:
  - match by SSID
  - and also support matching by full name when SSID not available
- Ambiguous matches must be logged.

## 15. Melody Department (መዝሙር) / Mezemran (መዘምራን) — MVP v1 Basics
### 15.1 Scope (MVP v1)
Membership management only:
- select / terminate / reselect Mezemran membership
- issue Mezemran ID (system generated)
- approvals + audit logs
- reports + exports (PDF/Excel)
No service operations (no schedules, rehearsals, assignments, service attendance) in MVP v1.

Constraint:
- Mezemran are selected only from SS students (SSStudentProfile).

### 15.2 Mezemran ID
Format:
`{SSAbbrev}MZ{YY}{RRR}`
- `YY` = last 2 digits of Mezmur entry Ethiopian year (year the student became Mezemran)
- `RRR` = 3-digit zero-padded roll number
Example (SSAbbrev=ABSS, Mezmur entry year 2018 EC): `ABSSMZ18001`

Rules:
- generated automatically by the system
- roll number auto-increments and is unique per Mezmur entry year (roll resets each year)

Mezemran ID must appear on:
- Student profile export PDF (yes)
- Separate Mezemran certificate/card PDF (yes)

### 15.3 Membership Lifecycle
Membership states (MVP v1):
- Active
- Terminated

Selection requirements:
- selection date (required)
- selected by user (required)
- reason/notes (required)
- criteria used (optional)

Termination requirements:
- termination date (required)
- terminated by user (required)
- termination reason (required)

Reselection:
- A terminated member can be reselected later
- membership history must be preserved as multiple records over time

Custom conditions:
- manual decision only (no rule engine in MVP v1)

### 15.4 Approval Workflow (Mezemran)
Selection / termination / reselection require approvals:
Draft (Melody Department Officer) → Melody Department Executive Approves → Executive Leader Final Approves

Rules:
- comments are required at approval steps
- timestamps are required
- After final approval, exports/printing are enabled.

### 15.5 Melody Reports & Exports (MVP v1)
Reports required:
- active Mezemran list
- terminated history list
- by grade/section breakdown
- by gender breakdown
Exports:
- printable list PDF/Excel
- Mezemran certificate/card PDF

Export formatting:
- signature/stamp placeholders like student export
- header/footer consistent with student export

## 16. Auditing & Logging (MVP v1)
“All kinds of logs” required:
- authentication events (login success/failure)
- CRUD actions on student profiles
- approval decisions (who/when/comment)
- transfers and grade/section changes
- attendance: create/edit/submit/approve, including edit reasons
- imports: file imported, results, errors
- Mezemran membership actions: select/terminate/reselect, approvals, exports

## 17. Data Retention Policy
- No deletion policy: records must not be physically deleted.
- Use deactivation/archival flags where needed.

## 18. Calendar & Date Handling
- System uses Ethiopian calendar in UI.
- Database stores Ethiopian date fields (year/month/day) and also stores derived Gregorian date for interoperability and querying.
- DoB and joined year are entered in Ethiopian calendar UI.

## 19. Deployment & Operations (MVP v1)
- Must run on-prem (church server) and also optionally on cloud.
- Must be usable offline within LAN (local IP/hostname) and also usable over internet when exposed.
- Dockerization required for both dev and production.
- Environments: dev and prod.
- CI/CD (GitHub):
  - tests on PR
  - linting on PR
  - build docker image
  - deploy on merge
- Backups required (strategy to be defined in implementation plan).

## 20. Open Items (Must be finalized in Phase 2)
- Canonical ID strategy for non-SS parish members (beyond SSID).
- Exact import date parsing rules for Ethiopian date inputs from exported files.
- Backup target details (external drive vs cloud).
- Final permission-to-API/UI mapping and role defaults assignment.
