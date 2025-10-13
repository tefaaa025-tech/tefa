# Overview

"دار الحياة" (Dar Alhayat) is a comprehensive desktop application for managing a psychiatric and addiction treatment facility. Built with PyQt6 and SQLite, it provides an Arabic-language interface for managing patients, payments, expenses, employees, and generating financial reports. The system tracks patient admissions, daily costs, cigarette allocations, payments, and produces detailed accounting statements.

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