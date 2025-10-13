import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QMessageBox, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, QCoreApplication, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QKeyEvent
import qdarkstyle
from typing import cast
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import Database
from modules.patients import PatientManager
from modules.payments import PaymentManager
from modules.expenses import ExpenseManager
from modules.employees import EmployeeManager
from modules.auth import AuthManager
from ui.dashboard import DashboardWidget
from ui.patients_widget import PatientsWidget
from ui.payments_widget import PaymentsWidget
from ui.expenses_widget import ExpensesWidget
from ui.employees_widget import EmployeesWidget
from ui.cigarettes_widget import CigarettesWidget
from ui.settings_widget import SettingsWidget
from ui.calculator_widget import CalculatorWidget
from ui.import_patients_widget import ImportPatientsWidget  # --- NEW FEATURE ---
from ui.text_editor_widget import TextEditorWidget  # --- NEW FEATURE ---

class LoginWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle('دار الحياة - تسجيل الدخول')
        self.setFixedSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 30, 40, 30)
        
        title1 = QLabel('دار الحياة')
        title1.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        title1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title1)
        
        title2 = QLabel('للطب النفسي وعلاج الإدمان')
        title2.setFont(QFont('Arial', 14))
        title2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title2)
        
        layout.addSpacing(30)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText('اسم المستخدم')
        self.username.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.username.setFixedHeight(40)
        layout.addWidget(self.username)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText('كلمة المرور')
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.password.setFixedHeight(40)
        self.password.returnPressed.connect(self.login)
        layout.addWidget(self.password)
        
        layout.addSpacing(10)
        
        login_btn = QPushButton('دخول')
        login_btn.setFixedHeight(45)
        login_btn.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username.text()
        password = self.password.text()
        
        auth_mgr = AuthManager(self.main_app.db)
        user = auth_mgr.authenticate(username, password)
        
        if user:
            self.main_app.current_user = user
            self.main_app.show_main_window()
            self.close()
        else:
            QMessageBox.warning(self, 'خطأ', 'اسم المستخدم أو كلمة المرور غير صحيحة')

class MainWindow(QMainWindow):
    def __init__(self, current_user=None):  # --- NEW FEATURE: User Permissions ---
        super().__init__()
        self.current_user = current_user  # --- NEW FEATURE: User Permissions ---
        self.db = Database('dar_alhayat_accounting/db/dar_alhayat.db')
        self.patient_mgr = PatientManager(self.db)
        self.payment_mgr = PaymentManager(self.db)
        self.expense_mgr = ExpenseManager(self.db)
        self.employee_mgr = EmployeeManager(self.db)
        self.current_theme = 'dark'
        self.sidebar_widget = None
        self.is_fullscreen = False
        
        self.setWindowTitle('دار الحياة - نظام المحاسبة')
        self.setMinimumSize(1200, 700)
        self.setup_ui()
        self.setup_auto_save()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.stacked_widget = QStackedWidget()
        
        self.dashboard = DashboardWidget(self.db, self.patient_mgr, 
                                        self.payment_mgr, self.expense_mgr, 
                                        self.employee_mgr)
        # --- NEW FEATURE: Pass current_user to widgets for permission checks ---
        self.patients_widget = PatientsWidget(self.db, self.patient_mgr, self.payment_mgr, self.current_user)
        self.payments_widget = PaymentsWidget(self.db, self.payment_mgr, self.patient_mgr, self.current_user)
        self.expenses_widget = ExpensesWidget(self.db, self.expense_mgr, self.current_user)
        self.employees_widget = EmployeesWidget(self.db, self.employee_mgr, self.current_user)
        self.cigarettes_widget = CigarettesWidget(self.db, self.patient_mgr, self.current_user)  # --- FIX (تمرير المستخدم الحالي) ---
        self.import_patients_widget = ImportPatientsWidget(self.db, self.patient_mgr)  # --- NEW FEATURE ---
        self.text_editor_widget = TextEditorWidget()  # --- NEW FEATURE ---
        self.calculator_widget = CalculatorWidget()
        self.settings_widget = SettingsWidget(self.db)
        self.settings_widget.theme_changed.connect(self.change_theme)
        
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.addWidget(self.patients_widget)
        self.stacked_widget.addWidget(self.payments_widget)
        self.stacked_widget.addWidget(self.expenses_widget)
        self.stacked_widget.addWidget(self.employees_widget)
        self.stacked_widget.addWidget(self.cigarettes_widget)
        self.stacked_widget.addWidget(self.import_patients_widget)  # --- NEW FEATURE ---
        self.stacked_widget.addWidget(self.text_editor_widget)  # --- NEW FEATURE ---
        self.stacked_widget.addWidget(self.calculator_widget)
        self.stacked_widget.addWidget(self.settings_widget)
        
        self.sidebar_widget = self.create_sidebar()
        
        main_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.sidebar_widget)
        
        central_widget.setLayout(main_layout)
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet('''
            QFrame {
                background-color: #2c3e50;
                border-left: 2px solid #34495e;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                text-align: right;
                padding: 15px 20px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        ''')
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(5)
        
        logo = QLabel('دار الحياة')
        logo.setFont(QFont('Arial', 20, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet('color: white; padding: 20px;')
        layout.addWidget(logo)
        
        buttons = [
            ('🏠 لوحة التحكم', 0),
            ('👥 المرضى', 1),
            ('💰 المدفوعات', 2),
            ('📊 المصروفات', 3),
            ('👔 الموظفين', 4),
            ('🚬 السجائر', 5),
            ('📥 استيراد من Excel', 6),  # --- NEW FEATURE ---
            ('📝 محرر النصوص', 7),  # --- NEW FEATURE ---
            ('🔢 آلة حاسبة', 8),
            ('⚙️ الإعدادات', 9),
        ]
        
        for text, index in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, i=index: self.change_page(i))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        exit_btn = QPushButton('🚪 خروج')
        exit_btn.clicked.connect(self.logout)  # --- FIX (تعديل زر الخروج ليعود للتسجيل) ---
        layout.addWidget(exit_btn)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.dashboard.refresh_data()
        elif index == 5:
            self.cigarettes_widget.load_cigarettes_data()
    
    def change_theme(self, theme_name):
        app = cast(QApplication, QApplication.instance())
        if not app:
            return
            
        if theme_name == 'الوضع الفاتح' and self.current_theme != 'light':
            self.current_theme = 'light'
            light_style = '''
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                    font-weight: 500;
                }
                QGroupBox {
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    margin-top: 12px;
                    padding: 18px;
                    background-color: #ffffff;
                    font-weight: bold;
                }
                QGroupBox::title {
                    color: #4a5bde;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px;
                    font-weight: bold;
                    font-size: 15px;
                }
                QPushButton {
                    background-color: #4a5bde;
                    color: #ffffff;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3d4bc7;
                }
                QPushButton:pressed {
                    background-color: #1abc9c;
                }
                QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 2px solid #c0c0c0;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 13px;
                }
                QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
                    border: 2px solid #4a5bde;
                }
                QComboBox::drop-down {
                    border: none;
                    padding-right: 10px;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    color: #000000;
                    selection-background-color: #4a5bde;
                    selection-color: #ffffff;
                    border: 2px solid #4a5bde;
                }
                QTableWidget {
                    background-color: #ffffff;
                    gridline-color: #c0c0c0;
                    border: 2px solid #c0c0c0;
                    border-radius: 6px;
                }
                QTableWidget::item {
                    color: #000000;
                    padding: 8px;
                    font-size: 13px;
                }
                QTableWidget::item:selected {
                    background-color: #4a5bde;
                    color: #ffffff;
                }
                QHeaderView::section {
                    background-color: #4a5bde;
                    color: #ffffff;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                }
                QScrollBar:vertical {
                    background-color: #f0f0f0;
                    width: 14px;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical {
                    background-color: #4a5bde;
                    border-radius: 7px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #3d4bc7;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QCheckBox {
                    color: #000000;
                    font-weight: 500;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #4a5bde;
                    border-radius: 4px;
                }
                QCheckBox::indicator:checked {
                    background-color: #4a5bde;
                }
                QRadioButton {
                    color: #000000;
                    font-weight: 500;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #4a5bde;
                    border-radius: 9px;
                }
                QRadioButton::indicator:checked {
                    background-color: #4a5bde;
                }
            '''
            app.setStyleSheet(light_style)
            
            if self.sidebar_widget:
                self.sidebar_widget.setStyleSheet('''
                    QFrame {
                        background-color: #667eea;
                        border-left: 2px solid #764ba2;
                    }
                    QPushButton {
                        background-color: transparent;
                        color: white;
                        text-align: right;
                        padding: 15px 20px;
                        border: none;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #764ba2;
                    }
                    QPushButton:pressed {
                        background-color: #1abc9c;
                    }
                ''')
        elif theme_name == 'الوضع الليلي' and self.current_theme != 'dark':
            self.current_theme = 'dark'
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
            
            if self.sidebar_widget:
                self.sidebar_widget.setStyleSheet('''
                    QFrame {
                        background-color: #2c3e50;
                        border-left: 2px solid #34495e;
                    }
                    QPushButton {
                        background-color: transparent;
                        color: white;
                        text-align: right;
                        padding: 15px 20px;
                        border: none;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #34495e;
                    }
                    QPushButton:pressed {
                        background-color: #1abc9c;
                    }
                ''')
    
    def setup_auto_save(self):
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save_database)
        self.auto_save_timer.start(300000)
    
    def auto_save_database(self):
        try:
            if self.db and self.db.conn:
                self.db.conn.commit()
                backup_dir = 'dar_alhayat_accounting/db/backups'
                os.makedirs(backup_dir, exist_ok=True)
                backup_file = os.path.join(
                    backup_dir, 
                    f'auto_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
                )
                shutil.copy2(self.db.db_path, backup_file)
                
                backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('auto_backup_')])
                if len(backups) > 10:
                    for old_backup in backups[:-10]:
                        os.remove(os.path.join(backup_dir, old_backup))
                
        except Exception as e:
            print(f'خطأ في الحفظ التلقائي: {str(e)}')
    
    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True
    
    def logout(self):
        # --- NEW (تسجيل الخروج والعودة لصفحة التسجيل) ---
        try:
            # Log logout to audit_log
            if self.current_user:
                user_id = self.current_user.get('id')
                username = self.current_user.get('username')
                
                query = '''
                    INSERT INTO audit_log (
                        user_id, username, action_type, action_description, created_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                '''
                self.db.execute(query, (
                    user_id,
                    username,
                    'تسجيل خروج',
                    f'قام المستخدم {username} بتسجيل الخروج',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
        except Exception as e:
            print(f'فشل تسجيل الخروج في audit_log: {str(e)}')
        
        # Close main window and show login
        app = QApplication.instance()
        if hasattr(app, 'show_login'):
            self.hide()
            app.login_window.show()
        else:
            self.close()
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        default_font = QFont("Arial", 12, QFont.Weight.Bold)
        self.setFont(default_font)
        
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        
        self.db = Database('dar_alhayat_accounting/db/dar_alhayat.db')
        auth_mgr = AuthManager(self.db)
        auth_mgr.initialize_default_users()
        
        self.current_user = None
        self.login_window = LoginWindow(self)
        self.main_window = None
    
    def show_login(self):
        self.login_window.show()
    
    def show_main_window(self):
        self.main_window = MainWindow(self.current_user)  # --- NEW FEATURE: User Permissions ---
        self.main_window.show()

if __name__ == '__main__':
    app = Application()
    app.show_login()
    sys.exit(app.exec())
