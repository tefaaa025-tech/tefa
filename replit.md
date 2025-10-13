# Overview

"دار الحياة" (Dar Alhayat) is a comprehensive desktop application for managing a psychiatric and addiction treatment facility. Built with PyQt6 and SQLite, it provides an Arabic-language interface for managing patients, payments, expenses, employees, and generating financial reports. The system tracks patient admissions, daily costs, cigarette allocations, payments, and produces detailed accounting statements.

## Recent Updates (October 2025)

### NEW FEATURES (Latest Update)

#### 1. Excel Import for Patients
- **Import Widget** (`ui/import_patients_widget.py`): New dedicated page for importing patients from Excel files
- **Features**:
  - Uses openpyxl/pandas for Excel file reading
  - Preview window showing valid and invalid records with error details
  - Batch insertion to database (50 records per batch)
  - Operation logging to `import_log.txt`
  - Safe error handling with try/except blocks
  - No impact on existing patient tables or interfaces

#### 2. User Permissions System
- **Role-Based Access Control**: Implemented permission checks based on user role
- **Two User Types**:
  - **Admin**: Full access (add, edit, delete, discharge)
  - **User**: Add-only access (cannot edit or delete)
- **Permission Enforcement**:
  - Protection in PatientsWidget for edit, delete, and discharge operations
  - Warning message: "⚠️ غير مصرح لك بتعديل أو حذف البيانات"
  - Backend validation prevents unauthorized operations even via shortcuts
- **Note**: PaymentsWidget, ExpensesWidget, and EmployeesWidget only support adding records (no edit/delete functionality), so they're automatically compliant

#### 3. Calculator Redesign
- **New Button Layout** (Left to Right):
  ```
  7 8 9
  4 5 6
  1 2 3
  0 . =
  ```
- **LTR Display**: Numbers displayed left-to-right for better readability
- **Simplified Design**: Removed extra operations, kept core functionality
- **No Logic Changes**: Mathematical operations work exactly as before

#### 4. Text Editor Widget
- **Professional Text Editor** (`ui/text_editor_widget.py`)
- **Features**:
  - Text formatting: Bold, Italic, Underline
  - Alignment: Left, Center, Right
  - Font selection and size control
  - Save as .txt or .docx files
  - Open previously saved files
  - Direct printing support
  - RTL support for Arabic text in Word documents

#### 5. Cigarette Price Update System
- **Impact Preview**: Shows confirmation dialog before price change with:
  - Old price vs new price comparison
  - Number of affected patients
  - Daily financial impact calculation
- **Automatic Recalculation**: Patient statements use new price immediately (calculated dynamically)
- **Change Logging**: All price changes logged to `cigarette_price_log.txt` with:
  - Timestamp
  - Old and new prices
  - Number of affected patients
  - Financial impact details
- **Important**: Patient statement costs are calculated on-demand, not stored. When price changes, all future calculations automatically use the new price.

### Authentication & Security
- **Bcrypt Password Hashing**: Implemented secure password storage using bcrypt encryption
- **New Users Created**: 
  - Admin user (username: admin, password: 1231)
  - Accountant user (username: user, password: 1)
- **Auth Module**: Created dedicated authentication manager (`modules/auth.py`) for user management
- **Permission System**: Role-based access control for sensitive operations

### UI/UX Enhancements
- **Bold Fonts**: Applied bold font styling (QFont.Weight.Bold) application-wide for better readability
- **Search Functionality**: Added search bars for patients with real-time filtering by name or phone
- **Filter & Sort Options**: 
  - Status filter (All, Active, Discharged)
  - Sort options (Alphabetical ascending/descending, Oldest first, Newest first)
- **Wider Table Columns**: Set fixed column widths for better data visibility (Name: 300px, Phone: 150px, etc.)
- **Auto-fit Button**: Added button to automatically resize columns to fit content

### Patient Management Improvements
- **Action Buttons**: Added edit (✏️), delete (🗑️), and discharge (🏁) buttons for each patient
- **Edit Patient**: Pre-filled dialog for updating patient information
- **Delete Patient**: Confirmation dialog before permanent deletion
- **Discharge Patient**: One-click patient discharge with automatic status update

### Cigarette Cost Calculation Fix
- **Accurate Formula**: Updated cigarette cost calculation to use `cigarettes_per_day * days * (cigarette_box_cost / cigarettes_per_box)`
- **New Settings**: Added `cigarette_box_cost` and `cigarettes_per_box` to settings table
- **Per-Patient Pricing**: System supports patient-specific cigarette pricing (priority over global settings)

### Database Management
- **Import Functionality**: Added database import feature with automatic backup and cleanup
- **Backup System**: Creates timestamped backups before any database replacement
- **Auto-cleanup**: Removes old database files while preserving the imported one
- **Settings Integration**: Database import button added to Settings page

### Technical Improvements
- **Environment Setup**: Updated to PyQt6 6.9.1+ for Qt 6.9 compatibility
- **System Dependencies**: Installed libxkbcommon, libGL, xorg packages for proper display
- **Xvfb Integration**: Configured virtual X server for VNC display support
- **Display Configuration**: Set DISPLAY=:99 for Replit VNC compatibility

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

**UI Framework**: PyQt6 with dark theme (qdarkstyle)
- **Main Window Structure**: Stacked widget pattern for multi-page navigation
- **Login System**: Simple authentication window before accessing main application
- **Key UI Components**:
  - Dashboard with statistics cards and matplotlib charts
  - Patient management with admission/discharge tracking
  - Payment tracking and receipt generation
  - Expense categorization and reporting
  - Employee management with transaction history
  - Cigarette inventory and pricing settings
  - Built-in calculator widget
  
**Design Patterns**:
- Right-to-left (RTL) layout for Arabic text support
- Responsive table widgets with custom headers
- Modal dialogs for data entry (Add/Edit operations)
- HTML-based report generation with print preview

## Backend Architecture

**Database Layer**: SQLite with direct SQL queries (no ORM)
- **Database Class** (`db/database.py`): Connection management and table creation
- **Manager Classes**: Business logic separation
  - `PatientManager`: Patient CRUD operations and status tracking
  - `PaymentManager`: Payment recording and revenue calculations
  - `ExpenseManager`: Expense categorization and aggregation
  - `EmployeeManager`: Employee records and salary transactions
  
**Data Model**:
- Patients: admission_date, department, daily_cost, cigarette tracking, discharge status
- Payments: patient-linked transactions with dates and notes
- Expenses: categorized spending with descriptions
- Employees: positions, salaries, and transaction history
- Settings: system configuration (cigarette pricing, etc.)

**Business Logic**:
- Patient status lifecycle: نشط (active) → متخرج (discharged)
- Daily cost calculation: (discharge_date - admission_date) × daily_cost
- Cigarette cost calculation: cigarettes_per_day × days × (box_cost / cigarettes_per_box)
- Revenue/expense aggregation by month and category

## Report Generation

**HTML-Based Reports**: Generated in-memory and opened in browser
- Patient account statements with itemized costs
- Daily financial summaries
- Monthly revenue/expense reports
- Custom date range filtering

**Export Capabilities**:
- Excel export using pandas/openpyxl
- Excel import for bulk patient data
- PDF generation support (reportlab in requirements)

## Text Processing

**Arabic Language Support**:
- arabic-reshaper: Proper Arabic character rendering
- python-bidi: Bidirectional text algorithm implementation
- RTL UI layouts throughout application

## Packaging

**Deployment**: PyInstaller for standalone executable
- Windows .exe generation with bundled resources
- Included assets: db folder, ui folder, modules, icon
- Single-file distribution option

# External Dependencies

## Core UI Framework
- **PyQt6**: Modern Qt6 Python bindings for desktop GUI
- **qdarkstyle**: Dark theme stylesheet for professional appearance

## Database
- **SQLite**: Embedded relational database (via Python stdlib)
- **sqlalchemy**: Listed but not actively used (direct sqlite3 queries instead)

## Data Processing
- **pandas**: DataFrame operations for Excel import/export
- **openpyxl**: Excel file format handling

## Visualization & Reports
- **matplotlib**: Chart generation for dashboard statistics
- **reportlab**: PDF report generation capabilities

## Security
- **bcrypt**: Password hashing for authentication system

## Text & Internationalization
- **arabic-reshaper**: Arabic text shaping for proper display
- **python-bidi**: Unicode bidirectional algorithm for RTL text

## Notes
- Application uses direct SQLite connections rather than SQLAlchemy ORM despite it being listed
- All UI text is in Arabic with RTL layout support
- Database schema is created programmatically on first run
- No external API integrations or cloud services currently implemented