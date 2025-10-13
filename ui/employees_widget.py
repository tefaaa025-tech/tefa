from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                             QLineEdit, QDateEdit, QMessageBox, QHeaderView, QComboBox,
                             QTextEdit, QFileDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
import os
import webbrowser
import tempfile

class AddEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('إضافة موظف جديد')
        self.setFixedSize(450, 450)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('اسم الموظف')
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('الاسم:'))
        layout.addWidget(self.name_input)
        
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText('المنصب')
        self.position_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('المنصب:'))
        layout.addWidget(self.position_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('رقم الهاتف')
        self.phone_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('الهاتف:'))
        layout.addWidget(self.phone_input)
        
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setDate(QDate.currentDate())
        self.hire_date_input.setCalendarPopup(True)
        layout.addWidget(QLabel('تاريخ التوظيف:'))
        layout.addWidget(self.hire_date_input)
        
        self.salary_input = QLineEdit()
        self.salary_input.setPlaceholderText('الراتب الأساسي')
        self.salary_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('الراتب الأساسي:'))
        layout.addWidget(self.salary_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('حفظ')
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('إلغاء')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'name': self.name_input.text(),
            'position': self.position_input.text(),
            'phone': self.phone_input.text(),
            'hire_date': self.hire_date_input.date().toString('yyyy-MM-dd'),
            'base_salary': float(self.salary_input.text()) if self.salary_input.text() else 0
        }

class AddTransactionDialog(QDialog):
    def __init__(self, employees, parent=None):
        super().__init__(parent)
        self.setWindowTitle('إضافة معاملة مالية للموظف')
        self.setFixedSize(450, 450)
        self.employees = employees
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.employee_combo = QComboBox()
        for employee in self.employees:
            self.employee_combo.addItem(f'{employee[1]} - {employee[2]}', employee[0])
        layout.addWidget(QLabel('الموظف:'))
        layout.addWidget(self.employee_combo)
        
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItems(['راتب', 'خصم', 'سلفة', 'مكافأة'])
        layout.addWidget(QLabel('نوع المعاملة:'))
        layout.addWidget(self.transaction_type_combo)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('المبلغ')
        self.amount_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('المبلغ:'))
        layout.addWidget(self.amount_input)
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        layout.addWidget(QLabel('التاريخ:'))
        layout.addWidget(self.date_input)
        
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText('ملاحظات (اختياري)')
        self.notes_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('ملاحظات:'))
        layout.addWidget(self.notes_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('حفظ')
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('إلغاء')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'employee_id': self.employee_combo.currentData(),
            'transaction_type': self.transaction_type_combo.currentText(),
            'amount': float(self.amount_input.text()) if self.amount_input.text() else 0,
            'transaction_date': self.date_input.date().toString('yyyy-MM-dd'),
            'notes': self.notes_input.text()
        }

class EmployeeDetailsDialog(QDialog):
    def __init__(self, employee, transactions, balance, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'تفاصيل الموظف - {employee[1]}')
        self.setMinimumSize(700, 500)
        self.employee = employee
        self.transactions = transactions
        self.balance = balance
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        info_label = QLabel(f'''
        <div style="text-align: right; direction: rtl;">
        <h2>{self.employee[1]}</h2>
        <p><b>المنصب:</b> {self.employee[2] if self.employee[2] else 'غير محدد'}</p>
        <p><b>الهاتف:</b> {self.employee[3] if self.employee[3] else 'غير محدد'}</p>
        <p><b>تاريخ التوظيف:</b> {self.employee[4]}</p>
        <p><b>الراتب الأساسي:</b> {self.employee[5]:.2f} جنيه</p>
        </div>
        ''')
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)
        
        balance_label = QLabel(f'''
        <div style="text-align: right; direction: rtl; background-color: #34495e; padding: 10px; border-radius: 5px;">
        <h3>الملخص المالي</h3>
        <p><b>إجمالي الرواتب المدفوعة:</b> {self.balance['salary_paid']:.2f} جنيه</p>
        <p><b>المكافآت:</b> {self.balance['bonuses']:.2f} جنيه</p>
        <p><b>الخصومات:</b> {self.balance['deductions']:.2f} جنيه</p>
        <p><b>السلف:</b> {self.balance['advances']:.2f} جنيه</p>
        <p style="color: #1abc9c;"><b>الصافي:</b> {self.balance['total']:.2f} جنيه</p>
        </div>
        ''')
        balance_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(balance_label)
        
        trans_label = QLabel('المعاملات المالية:')
        trans_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        layout.addWidget(trans_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.trans_table = QTableWidget()
        self.trans_table.setColumnCount(5)
        self.trans_table.setHorizontalHeaderLabels([
            'الرقم', 'النوع', 'المبلغ', 'التاريخ', 'ملاحظات'
        ])
        self.trans_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trans_table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.trans_table.setRowCount(len(self.transactions))
        
        for row, trans in enumerate(self.transactions):
            self.trans_table.setItem(row, 0, QTableWidgetItem(str(trans[0])))
            self.trans_table.setItem(row, 1, QTableWidgetItem(trans[2]))
            self.trans_table.setItem(row, 2, QTableWidgetItem(f'{trans[3]:.2f}'))
            self.trans_table.setItem(row, 3, QTableWidgetItem(trans[4]))
            self.trans_table.setItem(row, 4, QTableWidgetItem(trans[5] if trans[5] else ''))
        
        layout.addWidget(self.trans_table)
        
        btn_layout = QHBoxLayout()
        
        print_btn = QPushButton('🖨️ طباعة / حفظ PDF')
        print_btn.clicked.connect(self.print_statement)
        btn_layout.addWidget(print_btn)
        
        close_btn = QPushButton('إغلاق')
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def print_statement(self):
        try:
            transactions_rows = ''
            for trans in self.transactions:
                notes = trans[5] if trans[5] else '-'
                transactions_rows += f'''
                <tr>
                    <td>{trans[0]}</td>
                    <td>{trans[2]}</td>
                    <td>{trans[3]:.2f} جنيه</td>
                    <td>{trans[4]}</td>
                    <td>{notes}</td>
                </tr>
                '''
            
            html_content = f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>كشف حساب الموظف - {self.employee[1]}</title>
    <style>
        @media print {{
            body {{
                margin: 0;
                padding: 20px;
            }}
            .no-print {{
                display: none;
            }}
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            direction: rtl;
            text-align: right;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            margin: 0;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #667eea;
            margin: 0;
            font-size: 32px;
            font-weight: bold;
        }}
        
        .header h2 {{
            color: #764ba2;
            margin: 10px 0 0 0;
            font-size: 24px;
        }}
        
        .info-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .info-section h3 {{
            color: #667eea;
            margin-top: 0;
        }}
        
        .info-section p {{
            margin: 8px 0;
            font-size: 15px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        
        .stat-card.warning {{
            background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
        }}
        
        .stat-card.danger {{
            background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        }}
        
        .stat-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .stat-card .value {{
            font-size: 24px;
            font-weight: bold;
            margin: 0;
        }}
        
        .details-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .details-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: bold;
        }}
        
        .details-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
            text-align: center;
        }}
        
        .details-table tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #666;
            font-size: 14px;
        }}
        
        .print-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            margin: 20px auto;
            display: block;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }}
        
        .print-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 دار الحياة للطب النفسي وعلاج الإدمان</h1>
            <h2>👔 كشف حساب الموظف</h2>
            <div class="date">تاريخ الطباعة: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        
        <div class="info-section">
            <h3>معلومات الموظف</h3>
            <p><strong>الاسم:</strong> {self.employee[1]}</p>
            <p><strong>المنصب:</strong> {self.employee[2] if self.employee[2] else 'غير محدد'}</p>
            <p><strong>الهاتف:</strong> {self.employee[3] if self.employee[3] else 'غير محدد'}</p>
            <p><strong>تاريخ التوظيف:</strong> {self.employee[4]}</p>
            <p><strong>الراتب الأساسي:</strong> {self.employee[5]:.2f} جنيه</p>
        </div>
        
        <h3 style="color: #667eea; margin-top: 30px;">💰 الملخص المالي</h3>
        <div class="stats-grid">
            <div class="stat-card success">
                <h3>الرواتب المدفوعة</h3>
                <div class="value">{self.balance["salary_paid"]:.2f}</div>
                <p style="margin-top: 5px; font-size: 12px;">جنيه</p>
            </div>
            <div class="stat-card success">
                <h3>المكافآت</h3>
                <div class="value">{self.balance["bonuses"]:.2f}</div>
                <p style="margin-top: 5px; font-size: 12px;">جنيه</p>
            </div>
            <div class="stat-card danger">
                <h3>الخصومات</h3>
                <div class="value">{self.balance["deductions"]:.2f}</div>
                <p style="margin-top: 5px; font-size: 12px;">جنيه</p>
            </div>
            <div class="stat-card warning">
                <h3>السلف</h3>
                <div class="value">{self.balance["advances"]:.2f}</div>
                <p style="margin-top: 5px; font-size: 12px;">جنيه</p>
            </div>
            <div class="stat-card">
                <h3>الصافي</h3>
                <div class="value">{self.balance["total"]:.2f}</div>
                <p style="margin-top: 5px; font-size: 12px;">جنيه</p>
            </div>
        </div>
        
        <h3 style="color: #667eea; margin-top: 40px;">📋 المعاملات المالية</h3>
        <table class="details-table">
            <tr>
                <th>الرقم</th>
                <th>نوع المعاملة</th>
                <th>المبلغ</th>
                <th>التاريخ</th>
                <th>ملاحظات</th>
            </tr>
            {transactions_rows}
        </table>
        
        <div class="footer">
            <p><strong>دار الحياة للطب النفسي وعلاج الإدمان</strong></p>
            <p>نظام المحاسبة الإلكتروني</p>
        </div>
        
        <button class="print-button no-print" onclick="window.print()">🖨️ طباعة الكشف</button>
    </div>
</body>
</html>'''
            
            temp_dir = tempfile.gettempdir()
            filename = os.path.join(temp_dir, f'employee_statement_{self.employee[1]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            webbrowser.open('file://' + os.path.abspath(filename))
            QMessageBox.information(self, 'نجح', 'تم فتح كشف الحساب في المتصفح')
            
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء إنشاء الكشف:\n{str(e)}')

class EmployeesWidget(QWidget):
    def __init__(self, db, employee_mgr, current_user=None):  # --- NEW FEATURE: User Permissions ---
        super().__init__()
        self.db = db
        self.employee_mgr = employee_mgr
        self.current_user = current_user  # --- NEW FEATURE: User Permissions ---
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel('إدارة الموظفين')
        header.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        header.setStyleSheet('color: #1abc9c; padding: 20px;')
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignRight)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton('➕ إضافة موظف جديد')
        add_btn.clicked.connect(self.add_employee)
        btn_layout.addWidget(add_btn)
        
        add_trans_btn = QPushButton('💰 إضافة معاملة مالية')
        add_trans_btn.clicked.connect(self.add_transaction)
        btn_layout.addWidget(add_trans_btn)
        
        refresh_btn = QPushButton('🔄 تحديث')
        refresh_btn.clicked.connect(self.load_employees)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'الرقم', 'الاسم', 'المنصب', 'الهاتف', 'تاريخ التوظيف', 'الراتب', 'إجراءات'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_employees()
    
    def add_employee(self):
        dialog = AddEmployeeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['name'] and data['base_salary'] > 0:
                self.employee_mgr.add_employee(
                    data['name'], data['position'], data['phone'],
                    data['hire_date'], data['base_salary']
                )
                QMessageBox.information(self, 'نجح', 'تم إضافة الموظف بنجاح')
                self.load_employees()
    
    def add_transaction(self):
        employees = self.employee_mgr.get_all_employees('نشط')
        if not employees:
            QMessageBox.warning(self, 'تنبيه', 'لا يوجد موظفون نشطون')
            return
        
        dialog = AddTransactionDialog(employees, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['amount'] > 0:
                self.employee_mgr.add_transaction(
                    data['employee_id'], data['transaction_type'],
                    data['amount'], data['transaction_date'], data['notes']
                )
                QMessageBox.information(self, 'نجح', 'تم إضافة المعاملة بنجاح')
                self.load_employees()
    
    def view_employee_details(self, employee_id):
        employee = self.employee_mgr.get_employee(employee_id)
        transactions = self.employee_mgr.get_employee_transactions(employee_id)
        balance = self.employee_mgr.calculate_employee_balance(employee_id)
        
        dialog = EmployeeDetailsDialog(employee, transactions, balance, self)
        dialog.exec()
    
    def load_employees(self):
        employees = self.employee_mgr.get_all_employees()
        self.table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            self.table.setItem(row, 0, QTableWidgetItem(str(employee[0])))
            self.table.setItem(row, 1, QTableWidgetItem(employee[1]))
            self.table.setItem(row, 2, QTableWidgetItem(employee[2] if employee[2] else ''))
            self.table.setItem(row, 3, QTableWidgetItem(employee[3] if employee[3] else ''))
            self.table.setItem(row, 4, QTableWidgetItem(employee[4]))
            self.table.setItem(row, 5, QTableWidgetItem(f'{employee[5]:.2f}'))
            
            details_btn = QPushButton('📊 التفاصيل')
            details_btn.clicked.connect(lambda checked, emp_id=employee[0]: self.view_employee_details(emp_id))
            self.table.setCellWidget(row, 6, details_btn)
