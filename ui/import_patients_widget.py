# --- NEW FEATURE: Import Patients from Excel ---
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QFileDialog, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import openpyxl
import pandas as pd
from datetime import datetime
import os

class ImportPatientsWidget(QWidget):
    def __init__(self, db, patient_mgr):
        super().__init__()
        self.db = db
        self.patient_mgr = patient_mgr
        self.valid_records = []
        self.invalid_records = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel('📥 استيراد المرضى من Excel')
        header.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        instructions = QLabel('''
        <div style="text-align: right; direction: rtl; padding: 10px;">
        <h3>تعليمات الاستيراد:</h3>
        <p>• يجب أن يحتوي ملف Excel على الأعمدة التالية:</p>
        <p style="margin-right: 20px;">الاسم | هاتف الأهل | تاريخ الدخول | القسم | التكلفة اليومية | يستلم سجائر | عدد السجائر</p>
        <p>• تنسيق التاريخ: YYYY-MM-DD (مثال: 2024-01-15)</p>
        <p>• القسم: ديتوكس أو ريكفري</p>
        <p>• يستلم سجائر: 1 (نعم) أو 0 (لا)</p>
        </div>
        ''')
        instructions.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(instructions)
        
        buttons_layout = QHBoxLayout()
        
        select_file_btn = QPushButton('📂 اختيار ملف Excel')
        select_file_btn.clicked.connect(self.select_file)
        select_file_btn.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        buttons_layout.addWidget(select_file_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Preview group
        preview_group = QGroupBox('معاينة البيانات')
        preview_layout = QVBoxLayout()
        
        self.stats_label = QLabel('لم يتم تحميل أي ملف بعد')
        self.stats_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        preview_layout.addWidget(self.stats_label)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(8)
        self.preview_table.setHorizontalHeaderLabels([
            'الحالة', 'الاسم', 'هاتف الأهل', 'تاريخ الدخول', 
            'القسم', 'التكلفة اليومية', 'يستلم سجائر', 'عدد السجائر'
        ])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.preview_table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        preview_layout.addWidget(self.preview_table)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Error log group
        error_group = QGroupBox('سجل الأخطاء')
        error_layout = QVBoxLayout()
        
        self.error_log = QTextEdit()
        self.error_log.setReadOnly(True)
        self.error_log.setMaximumHeight(150)
        error_layout.addWidget(self.error_log)
        
        error_group.setLayout(error_layout)
        layout.addWidget(error_group)
        
        # Import button
        import_layout = QHBoxLayout()
        
        self.import_btn = QPushButton('✅ حفظ السجلات الصحيحة في قاعدة البيانات')
        self.import_btn.clicked.connect(self.import_records)
        self.import_btn.setEnabled(False)
        self.import_btn.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        self.import_btn.setStyleSheet('''
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        ''')
        import_layout.addWidget(self.import_btn)
        
        layout.addLayout(import_layout)
        self.setLayout(layout)
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'اختيار ملف Excel',
            '',
            'Excel Files (*.xlsx *.xls)'
        )
        
        if file_path:
            self.load_excel_file(file_path)
    
    def load_excel_file(self, file_path):
        try:
            self.valid_records = []
            self.invalid_records = []
            self.error_log.clear()
            
            # Read Excel file using pandas
            df = pd.read_excel(file_path)
            
            # Expected columns
            expected_columns = ['الاسم', 'هاتف الأهل', 'تاريخ الدخول', 'القسم', 
                              'التكلفة اليومية', 'يستلم سجائر', 'عدد السجائر']
            
            # Check if all columns exist
            missing_columns = [col for col in expected_columns if col not in df.columns]
            if missing_columns:
                QMessageBox.warning(
                    self, 
                    'خطأ', 
                    f'الأعمدة التالية مفقودة في الملف:\n{", ".join(missing_columns)}'
                )
                return
            
            # Validate and categorize records
            for index, row in df.iterrows():
                try:
                    # Validate name
                    name = str(row['الاسم']).strip()
                    if not name or name == 'nan':
                        raise ValueError('الاسم مطلوب')
                    
                    # Validate phone (optional)
                    phone = str(row['هاتف الأهل']).strip() if pd.notna(row['هاتف الأهل']) else ''
                    
                    # Validate admission date
                    admission_date = pd.to_datetime(row['تاريخ الدخول'])
                    admission_date_str = admission_date.strftime('%Y-%m-%d')
                    
                    # Validate department
                    department = str(row['القسم']).strip()
                    if department not in ['ديتوكس', 'ريكفري']:
                        raise ValueError('القسم يجب أن يكون ديتوكس أو ريكفري')
                    
                    # Validate daily cost
                    daily_cost = float(row['التكلفة اليومية'])
                    if daily_cost <= 0:
                        raise ValueError('التكلفة اليومية يجب أن تكون أكبر من صفر')
                    
                    # Validate cigarettes
                    receives_cigarettes = int(row['يستلم سجائر'])
                    if receives_cigarettes not in [0, 1]:
                        raise ValueError('يستلم سجائر يجب أن يكون 0 أو 1')
                    
                    cigarettes_count = int(row['عدد السجائر']) if receives_cigarettes == 1 else 0
                    if receives_cigarettes == 1 and cigarettes_count <= 0:
                        raise ValueError('عدد السجائر يجب أن يكون أكبر من صفر')
                    
                    # Valid record
                    self.valid_records.append({
                        'name': name,
                        'family_phone': phone,
                        'admission_date': admission_date_str,
                        'department': department,
                        'daily_cost': daily_cost,
                        'receives_cigarettes': receives_cigarettes,
                        'cigarettes_count': cigarettes_count,
                        'status': '✅ صحيح'
                    })
                    
                except Exception as e:
                    # Invalid record
                    self.invalid_records.append({
                        'name': str(row['الاسم']) if pd.notna(row['الاسم']) else 'غير محدد',
                        'family_phone': str(row['هاتف الأهل']) if pd.notna(row['هاتف الأهل']) else '',
                        'admission_date': str(row['تاريخ الدخول']) if pd.notna(row['تاريخ الدخول']) else '',
                        'department': str(row['القسم']) if pd.notna(row['القسم']) else '',
                        'daily_cost': str(row['التكلفة اليومية']) if pd.notna(row['التكلفة اليومية']) else '',
                        'receives_cigarettes': str(row['يستلم سجائر']) if pd.notna(row['يستلم سجائر']) else '',
                        'cigarettes_count': str(row['عدد السجائر']) if pd.notna(row['عدد السجائر']) else '',
                        'status': f'❌ خطأ: {str(e)}',
                        'error': str(e)
                    })
                    self.error_log.append(f'السطر {index + 2}: {str(row["الاسم"])} - {str(e)}')
            
            # Update UI
            self.update_preview()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                'خطأ',
                f'حدث خطأ أثناء قراءة الملف:\n{str(e)}'
            )
    
    def update_preview(self):
        total_records = len(self.valid_records) + len(self.invalid_records)
        valid_count = len(self.valid_records)
        invalid_count = len(self.invalid_records)
        
        self.stats_label.setText(
            f'إجمالي السجلات: {total_records} | '
            f'السجلات الصحيحة: ✅ {valid_count} | '
            f'السجلات الخاطئة: ❌ {invalid_count}'
        )
        
        # Display all records in table
        all_records = self.valid_records + self.invalid_records
        self.preview_table.setRowCount(len(all_records))
        
        for row, record in enumerate(all_records):
            status_item = QTableWidgetItem(record['status'])
            if '✅' in record['status']:
                status_item.setBackground(Qt.GlobalColor.green)
            else:
                status_item.setBackground(Qt.GlobalColor.red)
            
            self.preview_table.setItem(row, 0, status_item)
            self.preview_table.setItem(row, 1, QTableWidgetItem(record['name']))
            self.preview_table.setItem(row, 2, QTableWidgetItem(record['family_phone']))
            self.preview_table.setItem(row, 3, QTableWidgetItem(str(record['admission_date'])))
            self.preview_table.setItem(row, 4, QTableWidgetItem(str(record['department'])))
            self.preview_table.setItem(row, 5, QTableWidgetItem(str(record['daily_cost'])))
            self.preview_table.setItem(row, 6, QTableWidgetItem(str(record['receives_cigarettes'])))
            self.preview_table.setItem(row, 7, QTableWidgetItem(str(record['cigarettes_count'])))
        
        # Enable import button if there are valid records
        self.import_btn.setEnabled(len(self.valid_records) > 0)
    
    def import_records(self):
        if len(self.valid_records) == 0:
            QMessageBox.warning(self, 'تحذير', 'لا توجد سجلات صحيحة للاستيراد')
            return
        
        reply = QMessageBox.question(
            self,
            'تأكيد الاستيراد',
            f'هل أنت متأكد من استيراد {len(self.valid_records)} سجل إلى قاعدة البيانات؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Import in batches
                batch_size = 50
                imported_count = 0
                failed_count = 0
                
                for i in range(0, len(self.valid_records), batch_size):
                    batch = self.valid_records[i:i + batch_size]
                    
                    for record in batch:
                        try:
                            self.patient_mgr.add_patient(
                                record['name'],
                                record['family_phone'],
                                record['admission_date'],
                                record['department'],
                                record['daily_cost'],
                                record['receives_cigarettes'],
                                record['cigarettes_count']
                            )
                            imported_count += 1
                        except Exception as e:
                            failed_count += 1
                            self.error_log.append(f'فشل حفظ: {record["name"]} - {str(e)}')
                
                # Log the import operation
                self.log_import_operation(imported_count, failed_count)
                
                QMessageBox.information(
                    self,
                    'نجح',
                    f'تم استيراد {imported_count} سجل بنجاح\n'
                    f'فشل استيراد {failed_count} سجل'
                )
                
                # Reset
                self.valid_records = []
                self.invalid_records = []
                self.preview_table.setRowCount(0)
                self.stats_label.setText('تم الاستيراد بنجاح')
                self.import_btn.setEnabled(False)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'خطأ',
                    f'حدث خطأ أثناء الاستيراد:\n{str(e)}'
                )
    
    def log_import_operation(self, imported_count, failed_count):
        try:
            log_file = 'import_log.txt'
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f'\n=== استيراد المرضى - {timestamp} ===\n')
                f.write(f'عدد السجلات المستوردة: {imported_count}\n')
                f.write(f'عدد السجلات الفاشلة: {failed_count}\n')
                f.write('=' * 50 + '\n')
        except Exception as e:
            print(f'فشل تسجيل العملية: {str(e)}')
