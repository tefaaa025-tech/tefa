from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QGroupBox, QDateEdit, QSpinBox,
                             QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from modules.reports import ReportGenerator

class SettingsWidget(QWidget):
    theme_changed = pyqtSignal(str)
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel('الإعدادات')
        header.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        header.setStyleSheet('color: #1abc9c; padding: 20px;')
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignRight)
        
        theme_group = QGroupBox('المظهر')
        theme_layout = QVBoxLayout()
        
        theme_label = QLabel('الوضع:')
        theme_layout.addWidget(theme_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['الوضع الليلي', 'الوضع الفاتح'])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        reports_group = QGroupBox('التقارير')
        reports_layout = QVBoxLayout()
        
        daily_layout = QHBoxLayout()
        daily_label = QLabel('تقرير يومي:')
        daily_layout.addWidget(daily_label, alignment=Qt.AlignmentFlag.AlignRight)
        self.daily_date = QDateEdit()
        self.daily_date.setDate(QDate.currentDate())
        self.daily_date.setCalendarPopup(True)
        daily_layout.addWidget(self.daily_date)
        daily_btn = QPushButton('📄 إنشاء')
        daily_btn.clicked.connect(self.generate_daily_report)
        daily_layout.addWidget(daily_btn)
        reports_layout.addLayout(daily_layout)
        
        weekly_layout = QHBoxLayout()
        weekly_label = QLabel('تقرير أسبوعي:')
        weekly_layout.addWidget(weekly_label, alignment=Qt.AlignmentFlag.AlignRight)
        self.weekly_start = QDateEdit()
        self.weekly_start.setDate(QDate.currentDate().addDays(-7))
        self.weekly_start.setCalendarPopup(True)
        weekly_layout.addWidget(self.weekly_start)
        weekly_to_label = QLabel('إلى')
        weekly_layout.addWidget(weekly_to_label)
        self.weekly_end = QDateEdit()
        self.weekly_end.setDate(QDate.currentDate())
        self.weekly_end.setCalendarPopup(True)
        weekly_layout.addWidget(self.weekly_end)
        weekly_btn = QPushButton('📄 إنشاء')
        weekly_btn.clicked.connect(self.generate_weekly_report)
        weekly_layout.addWidget(weekly_btn)
        reports_layout.addLayout(weekly_layout)
        
        monthly_layout = QHBoxLayout()
        monthly_label = QLabel('تقرير شهري:')
        monthly_layout.addWidget(monthly_label, alignment=Qt.AlignmentFlag.AlignRight)
        self.monthly_month = QComboBox()
        self.monthly_month.addItems([
            'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ])
        self.monthly_month.setCurrentIndex(datetime.now().month - 1)
        monthly_layout.addWidget(self.monthly_month)
        self.monthly_year = QSpinBox()
        self.monthly_year.setRange(2000, 2100)
        self.monthly_year.setValue(datetime.now().year)
        monthly_layout.addWidget(self.monthly_year)
        monthly_btn = QPushButton('📄 إنشاء')
        monthly_btn.clicked.connect(self.generate_monthly_report)
        monthly_layout.addWidget(monthly_btn)
        reports_layout.addLayout(monthly_layout)
        
        yearly_layout = QHBoxLayout()
        yearly_label = QLabel('تقرير سنوي:')
        yearly_layout.addWidget(yearly_label, alignment=Qt.AlignmentFlag.AlignRight)
        self.yearly_year = QSpinBox()
        self.yearly_year.setRange(2000, 2100)
        self.yearly_year.setValue(datetime.now().year)
        yearly_layout.addWidget(self.yearly_year)
        yearly_btn = QPushButton('📄 إنشاء')
        yearly_btn.clicked.connect(self.generate_yearly_report)
        yearly_layout.addWidget(yearly_btn)
        reports_layout.addLayout(yearly_layout)
        
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)
        
        info_group = QGroupBox('معلومات البرنامج')
        info_layout = QVBoxLayout()
        
        info_text = QLabel('''
        <div style="text-align: right; direction: rtl;">
        <h3>دار الحياة - نظام المحاسبة</h3>
        <p>النسخة: 1.0.0</p>
        <p>تطبيق محاسبة متكامل لمؤسسة دار الحياة</p>
        <p>للطب النفسي وعلاج الإدمان</p>
        <br>
        <p>© 2025 جميع الحقوق محفوظة</p>
        </div>
        ''')
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def change_theme(self, theme):
        self.theme_changed.emit(theme)
    
    def generate_daily_report(self):
        if not self.db:
            QMessageBox.warning(self, 'خطأ', 'لم يتم تهيئة قاعدة البيانات')
            return
        
        date = self.daily_date.date().toString('yyyy-MM-dd')
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'حفظ التقرير اليومي', 
            f'تقرير_يومي_{date}.html',
            'HTML Files (*.html)'
        )
        
        if file_path:
            try:
                report_gen = ReportGenerator(self.db)
                report_gen.generate_daily_report(date, file_path)
                QMessageBox.information(self, 'نجح', f'تم إنشاء التقرير بنجاح في:\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء إنشاء التقرير:\n{str(e)}')
    
    def generate_weekly_report(self):
        if not self.db:
            QMessageBox.warning(self, 'خطأ', 'لم يتم تهيئة قاعدة البيانات')
            return
        
        start_date = self.weekly_start.date().toString('yyyy-MM-dd')
        end_date = self.weekly_end.date().toString('yyyy-MM-dd')
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'حفظ التقرير الأسبوعي', 
            f'تقرير_أسبوعي_{start_date}_إلى_{end_date}.html',
            'HTML Files (*.html)'
        )
        
        if file_path:
            try:
                report_gen = ReportGenerator(self.db)
                report_gen.generate_weekly_report(start_date, end_date, file_path)
                QMessageBox.information(self, 'نجح', f'تم إنشاء التقرير بنجاح في:\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء إنشاء التقرير:\n{str(e)}')
    
    def generate_monthly_report(self):
        if not self.db:
            QMessageBox.warning(self, 'خطأ', 'لم يتم تهيئة قاعدة البيانات')
            return
        
        month = self.monthly_month.currentIndex() + 1
        year = self.monthly_year.value()
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'حفظ التقرير الشهري', 
            f'تقرير_شهري_{year}_{month:02d}.html',
            'HTML Files (*.html)'
        )
        
        if file_path:
            try:
                report_gen = ReportGenerator(self.db)
                report_gen.generate_monthly_report(year, month, file_path)
                QMessageBox.information(self, 'نجح', f'تم إنشاء التقرير بنجاح في:\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء إنشاء التقرير:\n{str(e)}')
    
    def generate_yearly_report(self):
        if not self.db:
            QMessageBox.warning(self, 'خطأ', 'لم يتم تهيئة قاعدة البيانات')
            return
        
        year = self.yearly_year.value()
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'حفظ التقرير السنوي', 
            f'تقرير_سنوي_{year}.html',
            'HTML Files (*.html)'
        )
        
        if file_path:
            try:
                report_gen = ReportGenerator(self.db)
                report_gen.generate_yearly_report(year, file_path)
                QMessageBox.information(self, 'نجح', f'تم إنشاء التقرير بنجاح في:\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء إنشاء التقرير:\n{str(e)}')
