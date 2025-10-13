from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                             QLineEdit, QComboBox, QDateEdit, QCheckBox, QSpinBox,
                             QMessageBox, QFileDialog, QHeaderView, QScrollArea)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
import os
import webbrowser
import tempfile

class AddPatientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('إضافة مريض جديد')
        self.setFixedSize(500, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('اسم المريض')
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('الاسم:'))
        layout.addWidget(self.name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('رقم هاتف الأهل')
        self.phone_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('هاتف الأهل:'))
        layout.addWidget(self.phone_input)
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        layout.addWidget(QLabel('تاريخ الدخول:'))
        layout.addWidget(self.date_input)
        
        self.department_input = QComboBox()
        self.department_input.addItems(['ديتوكس', 'ريكفري'])
        layout.addWidget(QLabel('القسم:'))
        layout.addWidget(self.department_input)
        
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText('التكلفة اليومية')
        self.cost_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('التكلفة اليومية:'))
        layout.addWidget(self.cost_input)
        
        self.cigarettes_check = QCheckBox('يستلم سجائر')
        layout.addWidget(self.cigarettes_check)
        
        self.cigarettes_count = QSpinBox()
        self.cigarettes_count.setMaximum(100)
        self.cigarettes_count.setEnabled(False)
        self.cigarettes_check.toggled.connect(self.cigarettes_count.setEnabled)
        layout.addWidget(QLabel('عدد السجائر:'))
        layout.addWidget(self.cigarettes_count)
        
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
            'family_phone': self.phone_input.text(),
            'admission_date': self.date_input.date().toString('yyyy-MM-dd'),
            'department': self.department_input.currentText(),
            'daily_cost': float(self.cost_input.text()) if self.cost_input.text() else 0,
            'receives_cigarettes': 1 if self.cigarettes_check.isChecked() else 0,
            'cigarettes_count': self.cigarettes_count.value()
        }

class PatientStatementDialog(QDialog):
    def __init__(self, statement, parent=None):
        super().__init__(parent)
        self.statement = statement
        patient = statement['patient']
        self.setWindowTitle(f'كشف حساب المريض - {patient[1]}')
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        patient = self.statement['patient']
        
        info_html = f'''
        <div style="text-align: right; direction: rtl;">
        <h2 style="color: #1abc9c;">كشف حساب تفصيلي</h2>
        <h3>{patient[1]}</h3>
        <p><b>رقم الهاتف:</b> {patient[2] if patient[2] else 'غير محدد'}</p>
        <p><b>تاريخ الدخول:</b> {self.statement['admission_date'].strftime('%Y-%m-%d')}</p>
        <p><b>القسم:</b> {patient[4]}</p>
        <p><b>الحالة:</b> {patient[8]}</p>
        '''
        
        if self.statement['discharge_date']:
            info_html += f'<p><b>تاريخ التخرج:</b> {self.statement["discharge_date"].strftime("%Y-%m-%d")}</p>'
        
        info_html += f'''
        <p><b>عدد الأيام:</b> {self.statement['days']} يوم</p>
        </div>
        '''
        
        info_label = QLabel(info_html)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(info_label)
        
        expenses_html = f'''
        <div style="text-align: right; direction: rtl; background-color: #34495e; padding: 15px; border-radius: 5px; margin: 10px 0;">
        <h3 style="color: #1abc9c;">المصروفات</h3>
        <p><b>تكلفة الإقامة:</b> {self.statement['accommodation_cost']:.2f} جنيه ({self.statement['days']} يوم × {patient[5]:.2f} جنيه)</p>
        '''
        
        if self.statement['cigarettes_cost'] > 0:
            expenses_html += f'<p><b>تكلفة السجائر:</b> {self.statement["cigarettes_cost"]:.2f} جنيه</p>'
        
        expenses_html += f'''
        <p style="color: #e74c3c; font-size: 16px;"><b>إجمالي المصروفات:</b> {self.statement['total_expenses']:.2f} جنيه</p>
        </div>
        '''
        
        expenses_label = QLabel(expenses_html)
        expenses_label.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(expenses_label)
        
        payments_label = QLabel('<h3 style="text-align: right; color: #1abc9c;">المدفوعات:</h3>')
        payments_label.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(payments_label)
        
        payments_table = QTableWidget()
        payments_table.setColumnCount(3)
        payments_table.setHorizontalHeaderLabels(['التاريخ', 'المبلغ', 'ملاحظات'])
        payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        payments_table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        payments_table.setRowCount(len(self.statement['payments']))
        
        for row, payment in enumerate(self.statement['payments']):
            payments_table.setItem(row, 0, QTableWidgetItem(payment[0]))
            payments_table.setItem(row, 1, QTableWidgetItem(f'{payment[1]:.2f}'))
            payments_table.setItem(row, 2, QTableWidgetItem(payment[2] if payment[2] else ''))
        
        content_layout.addWidget(payments_table)
        
        summary_html = f'''
        <div style="text-align: right; direction: rtl; background-color: #2c3e50; padding: 15px; border-radius: 5px; margin: 10px 0;">
        <h3 style="color: #1abc9c;">الملخص النهائي</h3>
        <p><b>إجمالي المصروفات:</b> {self.statement['total_expenses']:.2f} جنيه</p>
        <p><b>إجمالي المدفوعات:</b> {self.statement['total_paid']:.2f} جنيه</p>
        <p style="font-size: 18px; color: {'#e74c3c' if self.statement['balance'] > 0 else '#1abc9c'};"><b>المتبقي:</b> {self.statement['balance']:.2f} جنيه</p>
        </div>
        '''
        
        summary_label = QLabel(summary_html)
        summary_label.setTextFormat(Qt.TextFormat.RichText)
        content_layout.addWidget(summary_label)
        
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
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
            patient = self.statement['patient']
            
            payments_rows = ''
            for payment in self.statement['payments']:
                notes = payment[2] if payment[2] else '-'
                payments_rows += f'''
                <tr>
                    <td>{payment[0]}</td>
                    <td>{payment[1]:.2f} جنيه</td>
                    <td>{notes}</td>
                </tr>
                '''
            
            discharge_info = ''
            if self.statement['discharge_date']:
                discharge_info = f'<p><strong>تاريخ التخرج:</strong> {self.statement["discharge_date"].strftime("%Y-%m-%d")}</p>'
            
            cigarettes_info = ''
            if self.statement['cigarettes_cost'] > 0:
                cigarettes_info = f'<p><strong>تكلفة السجائر:</strong> {self.statement["cigarettes_cost"]:.2f} جنيه</p>'
            
            html_content = f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>كشف حساب المريض - {patient[1]}</title>
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
        
        .expenses-section {{
            background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .expenses-section h3 {{
            margin-top: 0;
        }}
        
        .expenses-section p {{
            margin: 8px 0;
            font-size: 15px;
        }}
        
        .summary-section {{
            background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
            text-align: center;
        }}
        
        .summary-section h3 {{
            margin: 0 0 15px 0;
            font-size: 24px;
        }}
        
        .summary-section .balance {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
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
            <h2>📋 كشف حساب تفصيلي</h2>
            <div style="color: #666; font-size: 14px; margin-top: 10px;">تاريخ الطباعة: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        
        <div class="info-section">
            <h3>معلومات المريض</h3>
            <p><strong>الاسم:</strong> {patient[1]}</p>
            <p><strong>رقم الهاتف:</strong> {patient[2] if patient[2] else 'غير محدد'}</p>
            <p><strong>تاريخ الدخول:</strong> {self.statement["admission_date"].strftime('%Y-%m-%d')}</p>
            {discharge_info}
            <p><strong>القسم:</strong> {patient[4]}</p>
            <p><strong>الحالة:</strong> {patient[8]}</p>
            <p><strong>عدد الأيام:</strong> {self.statement['days']} يوم</p>
        </div>
        
        <div class="expenses-section">
            <h3>💸 المصروفات</h3>
            <p><strong>تكلفة الإقامة:</strong> {self.statement["accommodation_cost"]:.2f} جنيه ({self.statement['days']} يوم × {patient[5]:.2f} جنيه)</p>
            {cigarettes_info}
            <p style="font-size: 18px; margin-top: 15px;"><strong>إجمالي المصروفات:</strong> {self.statement['total_expenses']:.2f} جنيه</p>
        </div>
        
        <h3 style="color: #667eea; margin-top: 40px;">💰 سجل المدفوعات</h3>
        <table class="details-table">
            <tr>
                <th>التاريخ</th>
                <th>المبلغ</th>
                <th>ملاحظات</th>
            </tr>
            {payments_rows}
            <tr style="background-color: #f8f9fa; font-weight: bold;">
                <td>الإجمالي</td>
                <td>{self.statement['total_paid']:.2f} جنيه</td>
                <td>-</td>
            </tr>
        </table>
        
        <div class="summary-section">
            <h3>الحساب النهائي</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; text-align: center;">
                <div>
                    <p style="margin: 0; font-size: 14px; opacity: 0.9;">إجمالي المصروفات</p>
                    <p style="font-size: 24px; font-weight: bold; margin: 5px 0;">{self.statement['total_expenses']:.2f} جنيه</p>
                </div>
                <div>
                    <p style="margin: 0; font-size: 14px; opacity: 0.9;">إجمالي المدفوعات</p>
                    <p style="font-size: 24px; font-weight: bold; margin: 5px 0;">{self.statement['total_paid']:.2f} جنيه</p>
                </div>
                <div>
                    <p style="margin: 0; font-size: 14px; opacity: 0.9;">المتبقي</p>
                    <p class="balance">{self.statement['balance']:.2f} جنيه</p>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>دار الحياة للطب النفسي وعلاج الإدمان</strong></p>
            <p>نظام المحاسبة الإلكتروني</p>
        </div>
        
        <button class="print-button no-print" onclick="window.print()">🖨️ طباعة الكشف</button>
    </div>
</body>
</html>'''
            
            temp_dir = tempfile.gettempdir()
            filename = os.path.join(temp_dir, f'patient_statement_{patient[1]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            webbrowser.open('file://' + os.path.abspath(filename))
            QMessageBox.information(self, 'نجح', 'تم فتح كشف الحساب في المتصفح')
            
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء إنشاء الكشف:\n{str(e)}')

class PatientsWidget(QWidget):
    def __init__(self, db, patient_mgr, payment_mgr, current_user=None):  # --- NEW FEATURE: User Permissions ---
        super().__init__()
        self.db = db
        self.patient_mgr = patient_mgr
        self.payment_mgr = payment_mgr
        self.current_user = current_user  # --- NEW FEATURE: User Permissions ---
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel('إدارة المرضى')
        header.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        header.setStyleSheet('color: #1abc9c; padding: 20px;')
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignRight)
        
        search_layout = QHBoxLayout()
        search_label = QLabel('🔍 بحث:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('ابحث بالاسم أو الهاتف...')
        self.search_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.search_input.textChanged.connect(self.search_patients)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_label)
        layout.addLayout(search_layout)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton('➕ إضافة مريض جديد')
        add_btn.clicked.connect(self.add_patient)
        btn_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('🔄 تحديث')
        refresh_btn.clicked.connect(self.load_patients)
        btn_layout.addWidget(refresh_btn)
        
        autofit_btn = QPushButton('📏 Auto-fit')
        autofit_btn.clicked.connect(lambda: self.table.resizeColumnsToContents())
        btn_layout.addWidget(autofit_btn)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['الكل', 'النشطون', 'الخريجون'])
        self.filter_combo.currentTextChanged.connect(self.load_patients)
        btn_layout.addWidget(self.filter_combo)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(['أبجدي (صاعد)', 'أبجدي (تنازلي)', 'الأقدم أولاً', 'الأحدث أولاً'])
        self.sort_combo.currentTextChanged.connect(self.load_patients)
        btn_layout.addWidget(self.sort_combo)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            'الرقم', 'الاسم', 'هاتف الأهل', 'تاريخ الدخول', 'القسم',
            'التكلفة اليومية', 'السجائر', 'العدد', 'الحالة', 'المتبقي', 'كشف الحساب', 'إجراءات'
        ])
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 80)
        self.table.setColumnWidth(7, 60)
        self.table.setColumnWidth(8, 100)
        self.table.setColumnWidth(9, 120)
        self.table.setColumnWidth(10, 120)
        self.table.setColumnWidth(11, 250)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_patients()
    
    def add_patient(self):
        dialog = AddPatientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['name']:
                self.patient_mgr.add_patient(
                    data['name'], data['family_phone'], data['admission_date'],
                    data['department'], data['daily_cost'], data['receives_cigarettes'],
                    data['cigarettes_count']
                )
                QMessageBox.information(self, 'نجح', 'تم إضافة المريض بنجاح')
                self.load_patients()
    
    def view_patient_statement(self, patient_id):
        statement = self.patient_mgr.get_patient_detailed_statement(patient_id)
        if statement:
            dialog = PatientStatementDialog(statement, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, 'خطأ', 'لم يتم العثور على بيانات المريض')
    
    def load_patients(self):
        filter_text = self.filter_combo.currentText() if hasattr(self, 'filter_combo') else 'الكل'
        sort_text = self.sort_combo.currentText() if hasattr(self, 'sort_combo') else 'الأحدث أولاً'
        
        if filter_text == 'النشطون':
            patients = self.patient_mgr.get_all_patients('نشط')
        elif filter_text == 'الخريجون':
            patients = self.patient_mgr.get_all_patients('متخرج')
        else:
            patients = self.patient_mgr.get_all_patients()
        
        patients = list(patients)
        if sort_text == 'أبجدي (صاعد)':
            patients.sort(key=lambda x: x[1])
        elif sort_text == 'أبجدي (تنازلي)':
            patients.sort(key=lambda x: x[1], reverse=True)
        elif sort_text == 'الأقدم أولاً':
            patients.sort(key=lambda x: x[3])
        else:
            patients.sort(key=lambda x: x[3], reverse=True)
        
        self.table.setRowCount(len(patients))
        
        for row, patient in enumerate(patients):
            balance = self.patient_mgr.get_patient_balance(patient[0])
            
            self.table.setItem(row, 0, QTableWidgetItem(str(patient[0])))
            self.table.setItem(row, 1, QTableWidgetItem(patient[1]))
            self.table.setItem(row, 2, QTableWidgetItem(patient[2]))
            self.table.setItem(row, 3, QTableWidgetItem(patient[3]))
            self.table.setItem(row, 4, QTableWidgetItem(patient[4]))
            self.table.setItem(row, 5, QTableWidgetItem(f'{patient[5]:.2f}'))
            self.table.setItem(row, 6, QTableWidgetItem('نعم' if patient[6] else 'لا'))
            self.table.setItem(row, 7, QTableWidgetItem(str(patient[7])))
            self.table.setItem(row, 8, QTableWidgetItem(patient[8]))
            self.table.setItem(row, 9, QTableWidgetItem(f'{balance:.2f}'))
            
            statement_btn = QPushButton('📊 كشف الحساب')
            statement_btn.clicked.connect(lambda checked, p_id=patient[0]: self.view_patient_statement(p_id))
            self.table.setCellWidget(row, 10, statement_btn)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton('✏️')
            edit_btn.setFixedWidth(35)
            edit_btn.clicked.connect(lambda checked, p_id=patient[0]: self.edit_patient(p_id))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton('🗑️')
            delete_btn.setFixedWidth(35)
            delete_btn.clicked.connect(lambda checked, p_id=patient[0]: self.delete_patient(p_id))
            actions_layout.addWidget(delete_btn)
            
            if patient[8] == 'نشط':
                discharge_btn = QPushButton('🏁')
                discharge_btn.setFixedWidth(35)
                discharge_btn.clicked.connect(lambda checked, p_id=patient[0]: self.discharge_patient(p_id))
                actions_layout.addWidget(discharge_btn)
            
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 11, actions_widget)
    
    def search_patients(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            phone_item = self.table.item(row, 2)
            if name_item and phone_item:
                name = name_item.text().lower()
                phone = phone_item.text().lower()
                if search_text in name or search_text in phone:
                    self.table.setRowHidden(row, False)
                else:
                    self.table.setRowHidden(row, True)
    
    def edit_patient(self, patient_id):
        # --- NEW FEATURE: Check user permissions ---
        if self.current_user and self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, 'تحذير', '⚠️ غير مصرح لك بتعديل أو حذف البيانات.')
            return
        
        patient = self.patient_mgr.get_patient(patient_id)
        if not patient:
            return
        
        dialog = AddPatientDialog(self)
        dialog.setWindowTitle('تعديل بيانات المريض')
        dialog.name_input.setText(patient[1])
        dialog.phone_input.setText(patient[2] if patient[2] else '')
        dialog.date_input.setDate(QDate.fromString(patient[3], 'yyyy-MM-dd'))
        dialog.department_input.setCurrentText(patient[4])
        dialog.cost_input.setText(str(patient[5]))
        dialog.cigarettes_check.setChecked(bool(patient[6]))
        dialog.cigarettes_count.setValue(patient[7])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.patient_mgr.update_patient(
                patient_id, data['name'], data['family_phone'],
                data['department'], data['daily_cost'],
                data['receives_cigarettes'], data['cigarettes_count']
            )
            QMessageBox.information(self, 'نجح', 'تم تحديث بيانات المريض بنجاح')
            self.load_patients()
    
    def delete_patient(self, patient_id):
        # --- NEW FEATURE: Check user permissions ---
        if self.current_user and self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, 'تحذير', '⚠️ غير مصرح لك بتعديل أو حذف البيانات.')
            return
        
        reply = QMessageBox.question(
            self, 'تأكيد الحذف',
            'هل أنت متأكد من حذف السجل نهائياً؟ هذا الإجراء لا يمكن التراجع عنه.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
                QMessageBox.information(self, 'نجح', 'تم حذف المريض بنجاح')
                self.load_patients()
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء الحذف:\n{str(e)}')
    
    def discharge_patient(self, patient_id):
        # --- NEW FEATURE: Check user permissions ---
        if self.current_user and self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, 'تحذير', '⚠️ غير مصرح لك بتعديل أو حذف البيانات.')
            return
        
        reply = QMessageBox.question(
            self, 'تأكيد التخريج',
            'هل أنت متأكد من تخريج هذا المريض؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.patient_mgr.discharge_patient(patient_id)
            QMessageBox.information(self, 'نجح', 'تم تخريج المريض بنجاح')
            self.load_patients()
