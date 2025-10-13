import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox

class DatabaseImportDialog(QDialog):
    def __init__(self, current_db_path, parent=None):
        super().__init__(parent)
        self.current_db_path = current_db_path
        self.setWindowTitle('استيراد قاعدة بيانات')
        self.setFixedSize(500, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        info_label = QLabel('''
        <div style="text-align: right; direction: rtl;">
        <h3>استيراد قاعدة بيانات جديدة</h3>
        <p><b>تنبيه:</b> سيتم:</p>
        <ul>
            <li>حفظ نسخة احتياطية من القاعدة الحالية</li>
            <li>حذف جميع قواعد البيانات القديمة</li>
            <li>استيراد القاعدة الجديدة</li>
        </ul>
        <p style="color: red;">هذا الإجراء لا يمكن التراجع عنه!</p>
        </div>
        ''')
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        import_btn = QPushButton('📁 اختر ملف قاعدة البيانات')
        import_btn.clicked.connect(self.import_database)
        layout.addWidget(import_btn)
        
        close_btn = QPushButton('إلغاء')
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def import_database(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'اختر ملف قاعدة البيانات',
            '',
            'Database Files (*.db *.sqlite);;All Files (*.*)'
        )
        
        if not file_path:
            return
        
        reply = QMessageBox.question(
            self,
            'تأكيد الاستيراد',
            'سيتم حذف كل قواعد البيانات القديمة والاحتفاظ بقاعدة البيانات الجديدة فقط. متأكد؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db_dir = os.path.dirname(self.current_db_path)
                backup_dir = os.path.join(db_dir, 'backups')
                os.makedirs(backup_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = os.path.join(backup_dir, f'backup_before_import_{timestamp}.db')
                
                if os.path.exists(self.current_db_path):
                    shutil.copy2(self.current_db_path, backup_file)
                
                import glob
                db_files = glob.glob('*.db') + glob.glob('*.sqlite')
                db_files += glob.glob('db/**/*.db', recursive=True)
                db_files += glob.glob('db/**/*.sqlite', recursive=True)
                
                for db_file in db_files:
                    if 'backup' not in db_file and os.path.abspath(db_file) != os.path.abspath(file_path):
                        try:
                            os.remove(db_file)
                        except:
                            pass
                
                shutil.copy2(file_path, self.current_db_path)
                
                QMessageBox.information(
                    self,
                    'نجح',
                    f'تم استيراد قاعدة البيانات بنجاح!\nتم حفظ نسخة احتياطية في:\n{backup_file}\n\nيرجى إعادة تشغيل التطبيق.'
                )
                self.accept()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'خطأ',
                    f'حدث خطأ أثناء استيراد قاعدة البيانات:\n{str(e)}'
                )
