# Frontend Requirements — SS-SPMS MVP v1

## 1. UI Separation: Student vs. Non-Student
To avoid confusion and ensure data integrity, the frontend must clearly distinguish between Sunday School Students and general Parish Christians.

### A. Record Entry Points
- **Register SS Student**: A dedicated flow that enforces strict validation on all required fields (DoB, Baptismal Name, Grade/Section, Photos, and Emergency Contacts).
- **Add Parish Member (Christian)**: A "lightweight" entry flow allowing partial records (e.g., name and phone only) for non-student profiles.

### B. Visual Cues
- **Badge Indicators**: Students should have a prominent "SS Student" badge in list views and profile headers.
- **Color Coding**: Distinct UI color accents (e.g., Green for Students, Blue for general Christians) to provide immediate context during navigation.
- **Empty State Management**: When viewing a general Christian record, have a clear action button: "Convert to Sunday School Student" to initiate the full registration flow.

## 2. Validation Modes
- **Strict Mode (Students)**: Form submission is blocked if ANY mandatory SS field is missing.
- **Relaxed Mode (Non-Students)**: Only core identity fields (First Name, Father's Name) are required at the DB level, allowing records to be built over time.

## 3. Ethiopian Calendar Integration
- **Date Pickers**: Custom widgets allowing selection in Ethiopian months/years.
- **Dual Display**: Where space permits, show both Ethiopian and Gregorian dates (e.g., "Tahsas 1, 2016 (Dec 10, 2023)").

## 4. Workflows & Approvals
- **Clear Status Bars**: Progress headers showing current state (Draft -> Pending HR -> Active).
- **Comment Prompts**: Modal dialogs that REQUIRE a comment when an executive is approving or rejecting an action.
