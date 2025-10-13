from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QLineEdit, QMessageBox, QDialog, QDialogButtonBox,
                             QSpinBox, QCheckBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime
import os
import webbrowser
import tempfile

class CigarettesWidget(QWidget):
    def __init__(self, db, patient_mgr):
        super().__init__()
        self.db = db
        self.patient_mgr = patient_mgr
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel('إدارة السجائر')
        header.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        price_frame = QFrame()
        price_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        price_layout = QHBoxLayout()
        
        price_label = QLabel('سعر علبة السجائر (20 سيجارة):')
        price_label.setFont(QFont('Arial', 12))
        price_layout.addWidget(price_label)
        
        self.price_input = QLineEdit()
        self.price_input.setFixedWidth(150)
        self.price_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        current_price = self.get_cigarette_price()
        self.price_input.setText(str(current_price))
        price_layout.addWidget(self.price_input)
        
        price_label2 = QLabel('جنيه')
        price_layout.addWidget(price_label2)
        
        save_price_btn = QPushButton('حفظ السعر')
        save_price_btn.clicked.connect(self.save_price)
        price_layout.addWidget(save_price_btn)
        
        price_layout.addStretch()
        price_frame.setLayout(price_layout)
        layout.addWidget(price_frame)
        
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_layout = QHBoxLayout()
        
        total_cigarettes = self.patient_mgr.get_total_cigarettes()
        total_packs = total_cigarettes / 20
        daily_cost = total_packs * current_price
        
        self.stat1_label = QLabel(f'إجمالي السجائر اليومية: {total_cigarettes} سيجارة')
        self.stat1_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        stats_layout.addWidget(self.stat1_label)
        
        self.stat2_label = QLabel(f'عدد العلب المطلوبة: {total_packs:.1f} علبة')
        self.stat2_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        stats_layout.addWidget(self.stat2_label)
        
        self.stat3_label = QLabel(f'التكلفة اليومية: {daily_cost:.2f} جنيه')
        self.stat3_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        stats_layout.addWidget(self.stat3_label)
        
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('🔄 تحديث')
        refresh_btn.clicked.connect(self.load_cigarettes_data)
        buttons_layout.addWidget(refresh_btn)
        
        print_btn = QPushButton('🖨️ طباعة كشف حساب اليوم')
        print_btn.clicked.connect(self.print_daily_report)
        buttons_layout.addWidget(print_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'رقم المريض', 'الاسم', 'القسم', 'عدد السجائر', 
            'عدد العلب', 'التكلفة اليومية', 'إجراءات'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_cigarettes_data()
    
    def get_cigarette_price(self):
        query = "SELECT setting_value FROM settings WHERE setting_key = 'cigarette_pack_price'"
        result = self.db.fetchone(query)
        return float(result[0]) if result else 40.0
    
    def save_price(self):
        try:
            new_price = float(self.price_input.text())
            if new_price <= 0:
                QMessageBox.warning(self, 'خطأ', 'السعر يجب أن يكون أكبر من صفر')
                return
            
            # --- NEW FEATURE: Show impact of price change ---
            old_price = self.get_cigarette_price()
            
            # Calculate affected patients and financial impact
            affected_patients_query = '''
                SELECT COUNT(*), SUM(cigarettes_count) 
                FROM patients 
                WHERE status = 'نشط' AND receives_cigarettes = 1
            '''
            result = self.db.fetchone(affected_patients_query)
            affected_count = result[0] if result else 0
            total_daily_cigarettes = result[1] if result and result[1] else 0
            
            # Calculate daily financial difference
            old_daily_cost = (total_daily_cigarettes / 20) * old_price
            new_daily_cost = (total_daily_cigarettes / 20) * new_price
            daily_difference = new_daily_cost - old_daily_cost
            
            # Show confirmation dialog
            price_change = new_price - old_price
            confirmation_msg = f'''
            <div style="text-align: right; direction: rtl;">
            <h3>تأكيد تغيير سعر السجائر</h3>
            <p><b>السعر القديم:</b> {old_price:.2f} جنيه</p>
            <p><b>السعر الجديد:</b> {new_price:.2f} جنيه</p>
            <p><b>الفرق:</b> {price_change:+.2f} جنيه</p>
            <br>
            <p><b>عدد المرضى المتأثرين:</b> {affected_count} مريض</p>
            <p><b>إجمالي السجائر اليومية:</b> {total_daily_cigarettes} سيجارة</p>
            <p><b>الفرق في التكلفة اليومية:</b> {daily_difference:+.2f} جنيه</p>
            <br>
            <p>⚠️ سيؤثر هذا التغيير على حساب تكلفة السجائر في كشوف حساب جميع المرضى الحاليين والمستقبليين.</p>
            <p>هل أنت متأكد من التغيير؟</p>
            </div>
            '''
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('تأكيد تغيير السعر')
            msg_box.setText(confirmation_msg)
            msg_box.setTextFormat(Qt.TextFormat.RichText)
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                # Update the price
                query = '''
                    UPDATE settings 
                    SET setting_value = ?, updated_at = ?
                    WHERE setting_key = 'cigarette_pack_price'
                '''
                self.db.execute(query, (str(new_price), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                # Log the price change
                self.log_price_change(old_price, new_price, affected_count, daily_difference)
                
                QMessageBox.information(self, 'نجح', 'تم حفظ السعر بنجاح وتسجيل التغيير')
                self.load_cigarettes_data()
            
        except ValueError:
            QMessageBox.warning(self, 'خطأ', 'الرجاء إدخال سعر صحيح')
    
    def log_price_change(self, old_price, new_price, affected_patients, daily_difference):
        # --- NEW FEATURE: Log price changes ---
        try:
            log_file = 'cigarette_price_log.txt'
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f'\n=== تغيير سعر السجائر - {timestamp} ===\n')
                f.write(f'السعر القديم: {old_price:.2f} جنيه\n')
                f.write(f'السعر الجديد: {new_price:.2f} جنيه\n')
                f.write(f'الفرق: {(new_price - old_price):+.2f} جنيه\n')
                f.write(f'عدد المرضى المتأثرين: {affected_patients}\n')
                f.write(f'الفرق في التكلفة اليومية: {daily_difference:+.2f} جنيه\n')
                f.write('=' * 60 + '\n')
        except Exception as e:
            print(f'فشل تسجيل تغيير السعر: {str(e)}')
    
    def load_cigarettes_data(self):
        query = '''
            SELECT id, name, department, cigarettes_count, receives_cigarettes 
            FROM patients 
            WHERE status = 'نشط'
            ORDER BY receives_cigarettes DESC, name
        '''
        patients = self.db.fetchall(query)
        
        cigarette_price = self.get_cigarette_price()
        
        self.table.setRowCount(len(patients))
        for row, patient in enumerate(patients):
            patient_id, name, department, cigarettes_count, receives_cigarettes = patient
            packs = cigarettes_count / 20
            daily_cost = packs * cigarette_price
            
            self.table.setItem(row, 0, QTableWidgetItem(str(patient_id)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(department))
            self.table.setItem(row, 3, QTableWidgetItem(str(cigarettes_count)))
            self.table.setItem(row, 4, QTableWidgetItem(f'{packs:.2f}'))
            self.table.setItem(row, 5, QTableWidgetItem(f'{daily_cost:.2f}'))
            
            if receives_cigarettes:
                action_btn = QPushButton('تعطيل السجائر')
                action_btn.setStyleSheet('background-color: #e74c3c; color: white;')
            else:
                action_btn = QPushButton('تفعيل السجائر')
                action_btn.setStyleSheet('background-color: #27ae60; color: white;')
            
            action_btn.clicked.connect(lambda checked, pid=patient_id, enabled=receives_cigarettes: self.toggle_cigarettes(pid, enabled))
            self.table.setCellWidget(row, 6, action_btn)
        
        total_cigarettes = self.patient_mgr.get_total_cigarettes()
        total_packs = total_cigarettes / 20
        daily_cost = total_packs * cigarette_price
        
        self.stat1_label.setText(f'إجمالي السجائر اليومية: {total_cigarettes} سيجارة')
        self.stat2_label.setText(f'عدد العلب المطلوبة: {total_packs:.1f} علبة')
        self.stat3_label.setText(f'التكلفة اليومية: {daily_cost:.2f} جنيه')
    
    def toggle_cigarettes(self, patient_id, currently_enabled):
        if currently_enabled:
            reply = QMessageBox.question(
                self, 'تأكيد', 
                'هل أنت متأكد من تعطيل السجائر لهذا المريض؟',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                query = '''
                    UPDATE patients 
                    SET receives_cigarettes = 0, cigarettes_count = 0
                    WHERE id = ?
                '''
                self.db.execute(query, (patient_id,))
                QMessageBox.information(self, 'نجح', 'تم تعطيل السجائر بنجاح')
                self.load_cigarettes_data()
        else:
            dialog = QDialog(self)
            dialog.setWindowTitle('تفعيل السجائر')
            dialog.setFixedWidth(300)
            
            layout = QVBoxLayout()
            
            label = QLabel('أدخل عدد السجائر اليومية:')
            layout.addWidget(label)
            
            count_input = QSpinBox()
            count_input.setMinimum(1)
            count_input.setMaximum(100)
            count_input.setValue(20)
            count_input.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(count_input)
            
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | 
                QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            dialog.setLayout(layout)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                cigarettes_count = count_input.value()
                query = '''
                    UPDATE patients 
                    SET receives_cigarettes = 1, cigarettes_count = ?
                    WHERE id = ?
                '''
                self.db.execute(query, (cigarettes_count, patient_id))
                QMessageBox.information(self, 'نجح', f'تم تفعيل السجائر بنجاح ({cigarettes_count} سيجارة يومياً)')
                self.load_cigarettes_data()
    
    def print_daily_report(self):
        try:
            cigarette_price = self.get_cigarette_price()
            
            query = '''
                SELECT id, name, department, cigarettes_count 
                FROM patients 
                WHERE status = 'نشط' AND receives_cigarettes = 1
                ORDER BY name
            '''
            patients = self.db.fetchall(query)
            
            total_cigarettes = 0
            total_cost = 0
            
            patients_table_rows = ''
            for patient in patients:
                patient_id, name, department, cigarettes_count = patient
                packs = cigarettes_count / 20
                daily_cost = packs * cigarette_price
                
                total_cigarettes += cigarettes_count
                total_cost += daily_cost
                
                patients_table_rows += f'''
                <tr>
                    <td>{patient_id}</td>
                    <td>{name}</td>
                    <td>{department}</td>
                    <td>{cigarettes_count}</td>
                    <td>{packs:.2f}</td>
                    <td>{daily_cost:.2f}</td>
                </tr>
                '''
            
            total_packs = total_cigarettes / 20
            
            html_content = f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير السجائر اليومي</title>
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
        
        .header .date {{
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
        
        .info-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .info-section p {{
            margin: 8px 0;
            font-size: 16px;
            font-weight: bold;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .stat-card .value {{
            font-size: 32px;
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
            padding: 15px;
            text-align: center;
            font-weight: bold;
        }}
        
        .details-table td {{
            padding: 12px 15px;
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
            <h2>🚬 تقرير السجائر اليومي</h2>
            <div class="date">تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        
        <div class="info-section">
            <p>📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}</p>
            <p>💰 سعر علبة السجائر (20 سيجارة): {cigarette_price:.2f} جنيه</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>إجمالي السجائر اليومية</h3>
                <div class="value">{total_cigarettes}</div>
                <p style="margin-top: 10px; font-size: 14px;">سيجارة</p>
            </div>
            <div class="stat-card">
                <h3>عدد العلب المطلوبة</h3>
                <div class="value">{total_packs:.1f}</div>
                <p style="margin-top: 10px; font-size: 14px;">علبة</p>
            </div>
            <div class="stat-card">
                <h3>التكلفة اليومية الإجمالية</h3>
                <div class="value">{total_cost:.2f}</div>
                <p style="margin-top: 10px; font-size: 14px;">جنيه</p>
            </div>
        </div>
        
        <h3 style="color: #667eea; margin-top: 40px;">📋 تفاصيل المرضى المستلمين للسجائر</h3>
        <table class="details-table">
            <tr>
                <th>رقم المريض</th>
                <th>الاسم</th>
                <th>القسم</th>
                <th>عدد السجائر</th>
                <th>عدد العلب</th>
                <th>التكلفة اليومية</th>
            </tr>
            {patients_table_rows}
        </table>
        
        <div class="footer">
            <p><strong>دار الحياة للطب النفسي وعلاج الإدمان</strong></p>
            <p>نظام المحاسبة الإلكتروني</p>
        </div>
        
        <button class="print-button no-print" onclick="window.print()">🖨️ طباعة التقرير</button>
    </div>
</body>
</html>'''
            
            temp_dir = tempfile.gettempdir()
            filename = os.path.join(temp_dir, f'cigarettes_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            webbrowser.open('file://' + os.path.abspath(filename))
            QMessageBox.information(self, 'نجح', 'تم فتح التقرير في المتصفح')
            
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء إنشاء التقرير:\n{str(e)}')
