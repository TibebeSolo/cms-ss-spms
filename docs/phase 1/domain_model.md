# Domain Model — SS-SPMS (MVP v1)
EOTC Sunday School Students Profile Management System — Single Parish

## 1. Bounded Contexts (Modular Monolith)
MVP v1 contexts:
- org: Parish + Sunday School profile
- identity: users, roles, permissions, authentication logs
- people: Christian (canonical person), contacts (lightweight), confession father (lightweight)
- sundayschool: SS student profile, grade/section, transfers, attendance, reports
- melody: Mezemran membership management (membership records + IDs + approvals + reports + exports)
- audit: audit log + import logs

## 2. Core Entity Summary (MVP v1)

### 2.1 Organization
Parish(id, name, address, phone, diocese_name)
SundaySchool(id, parish_id, name, abbreviation, phone, logo_url, social_links)

Constraint: 1 Parish → 1 SundaySchool.

### 2.2 Identity & Access Control
UserAccount(id, username, password_hash, is_active, failed_login_count, locked_until?, last_login_at?, created_at)
Role(id, name, is_system_role, description?)
Permission(id, code, description)
RolePermission(role_id, permission_id)
UserRole(user_id, role_id)
AuthEventLog(id, user_id?, username_attempted, event_type, ip_address?, user_agent?, timestamp)

Lockout constraint: after 7 failed attempts.

### 2.3 People
Christian(id, first_name, father_name, grandfather_name, baptismal_name?, sex?, dob_eth?, dob_greg?, phone?, email?, address..., photo_url?, ...)
Notes:
- Christian can exist without SSStudentProfile.
- SS student strict completeness is enforced via SSStudentProfile constraints + validation.

ConfessionFather(id, full_name, phone, servant_church, residence)

RelationshipType(id, name)  # customizable
ContactPerson(id, full_name, relationship_type_id, phone, address, linked_christian_id?)
StudentContactLink(id, ss_student_profile_id, contact_person_id, is_primary)

Constraints:
- Each SS student requires >= 1 contact (one primary required).
- ContactPerson can link to multiple students.

### 2.4 Sunday School Student Profile
SSStudentProfile(
  id,
  christian_id (1:1),
  ssid (unique; username for SS students),
  joined_year_eth,
  ss_roll_number (auto-increment; unique per joined year; display padded to 3 digits; resets yearly),
  grade_id,
  section_id,
  student_status_id,
  registration_state,
  profile_update_state,
  confession_father_id,
  created_at,
  updated_at
)

SSID generation rule:
- ssid = `{SSAbbrev}{YY}{RRR}`
  - YY = last 2 digits of joined_year_eth (Ethiopian)
  - RRR = 3-digit zero-padded roll
Example: ABSS11001

StudentStatus(defaults: Active, Transferred, Not Complete, Undetermined, Elders; customizable)

### 2.5 Grade/Section
Grade(id, name, order_no, is_custom)
Section(id, name, is_custom)
ClassGroup(id, grade_id, section_id, meeting_day_of_week, is_active)

Constraint: Student belongs to exactly one ClassGroup via Grade+Section fields.

### 2.6 Transfers
GradeSectionChangeRequest(
  id,
  ss_student_profile_id,
  from_grade_id, from_section_id,
  to_grade_id, to_section_id,
  reason,
  drafted_by_user_id, drafted_at,
  hr_approved_by_user_id?, hr_approved_at?, hr_comment (required when approving),
  leader_approved_by_user_id?, leader_approved_at?, leader_comment (required when approving),
  state
)

Approval chain same as registration.

### 2.7 Student Registration & Update Approval
StudentRegistrationRequest(
  id,
  ss_student_profile_id,
  drafted_by_user_id, drafted_at,
  hr_approved_by_user_id?, hr_approved_at?, hr_comment (required when approving),
  leader_approved_by_user_id?, leader_approved_at?, leader_comment (required when approving),
  state (DRAFT, PENDING_HR, PENDING_LEADER, ACTIVE, REJECTED)
)

StudentProfileUpdateRequest(
  id,
  ss_student_profile_id,
  changes_payload,
  drafted_by_user_id, drafted_at,
  hr_approved_by_user_id?, hr_approved_at?, hr_comment (required when approving),
  state (PENDING_HR, APPROVED, REJECTED)
)

### 2.8 Attendance
AttendanceSession(
  id,
  session_date_eth, session_date_greg,
  scope_type (CLASSGROUP/WHOLE_SS/SPECIAL_EVENT),
  class_group_id?,
  title?,
  event_type (REGULAR/SPECIAL),
  created_by_user_id,
  created_at,
  state (DRAFT/SUBMITTED/PENDING_APPROVAL/APPROVED)
)

AttendanceRecord(
  id,
  attendance_session_id,
  ss_student_profile_id,
  status (PRESENT/ABSENT/LATE/EXCUSED),
  note?,
  created_by_user_id,
  created_at,
  updated_at
)

AttendanceApproval(
  id,
  attendance_session_id,
  submitted_by_user_id, submitted_at,
  approved_by_user_id, approved_at,
  comment (required)
)

AttendanceEditLog(
  id,
  attendance_record_id,
  edited_by_user_id, edited_at,
  reason_note (required),
  before_snapshot,
  after_snapshot
)

Constraints:
- Unique(attendance_session_id, ss_student_profile_id)
- HR Expert cannot edit after submit; HR Executive can edit after approval but must log reason.

### 2.9 Imports
ImportRun(id, import_type, source, file_name, format, started_by_user_id, started_at, finished_at?, status, summary_counts)
ImportRowError(id, import_run_id, row_number, error_code, message, raw_payload)

Matching: SSID + full name fallback; ambiguous matches logged.

### 2.10 Melody Department (Mezemran)
MezemranMembership(
  id,
  ss_student_profile_id,   # must reference SS student only
  mezmur_entry_year_eth,
  mezemran_roll_number (auto-increment; unique per mezmur_entry_year_eth; display padded to 3 digits; resets yearly),
  mezemran_id (stored; generated),
  status (ACTIVE/TERMINATED),
  selected_at (required),
  selected_by_user_id (required),
  selection_reason (required),
  criteria_used? (optional),
  terminated_at?,
  terminated_by_user_id?,
  termination_reason?,
  created_at,
  updated_at
)

Mezemran ID generation rule:
- mezemran_id = `{SSAbbrev}MZ{YY}{RRR}`
  - YY = last 2 digits of mezmur_entry_year_eth (Ethiopian)
  - RRR = 3-digit zero-padded roll
Example: ABSSMZ18001

Constraints:
- Membership history is preserved: multiple records per student over time allowed.
- Only one ACTIVE membership per student at a time (enforce).
- Roll uniqueness scoped to mezmur_entry_year_eth.

MezemranChangeRequest(
  id,
  action_type (SELECT/TERMINATE/RESELECT),
  ss_student_profile_id,
  target_membership_id? (for terminate),
  payload (reason/notes/criteria),
  drafted_by_user_id (Melody Officer),
  drafted_at,
  melody_exec_approved_by_user_id?, melody_exec_approved_at?, melody_exec_comment (required when approving),
  leader_approved_by_user_id?, leader_approved_at?, leader_comment (required when approving),
  state (DRAFT/PENDING_MELODY_EXEC/PENDING_LEADER/APPROVED/REJECTED)
)

Rules:
- Approval chain: Melody Officer drafts → Melody Executive approves → Executive Leader final approves
- After final approval, membership changes applied and exports enabled.

### 2.11 Auditing
AuditLog(id, actor_user_id, action_type, entity_type, entity_id, timestamp, metadata)

Policy:
- Audit everything: registration, approvals, attendance, edits, imports, Mezemran actions, exports, auth events.

## 3. Ethiopian Date Value Object
EthiopianDate(year, month, day) stored + derived gregorian_date.
All date entry is Ethiopian in UI; DB stores both Ethiopian fields and derived Gregorian.

## 4. Notes for Phase 2 (Implementation Planning)
- Permission inventory is explicitly custom (fixed codes) + model permissions.
- Export templates: student profile, Mezemran certificate/card, Mezemran list reports must share header/footer/signature/stamp placeholders.
- Offline LAN deployment and backup strategy must be specified.
