from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StatCard(QFrame):
    def __init__(self, title, value, icon=''):
        super().__init__()
        self.setStyleSheet('''
            QFrame {
                background-color: #34495e;
                border-radius: 10px;
                padding: 15px;
            }
        ''')
        
        layout = QVBoxLayout()
        
        title_label = QLabel(f'{icon} {title}')
        title_label.setFont(QFont('Arial', 12))
        title_label.setStyleSheet('color: #95a5a6;')
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont('Arial', 28, QFont.Weight.Bold))
        self.value_label.setStyleSheet('color: #1abc9c;')
        layout.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
    
    def update_value(self, value):
        self.value_label.setText(str(value))

class DashboardWidget(QWidget):
    def __init__(self, db, patient_mgr, payment_mgr, expense_mgr, employee_mgr):
        super().__init__()
        self.db = db
        self.patient_mgr = patient_mgr
        self.payment_mgr = payment_mgr
        self.expense_mgr = expense_mgr
        self.employee_mgr = employee_mgr
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel('لوحة التحكم الرئيسية')
        header.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        header.setStyleSheet('color: #1abc9c; padding: 20px;')
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignRight)
        
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.active_patients_card = StatCard('المرضى النشطون', '0', '👥')
        self.graduated_card = StatCard('الخريجون', '0', '🎓')
        self.revenue_card = StatCard('إجمالي الإيرادات', '0 جنيه', '💰')
        self.expenses_card = StatCard('إجمالي المصروفات', '0 جنيه', '📊')
        self.profit_card = StatCard('صافي الربح', '0 جنيه', '📈')
        self.employees_card = StatCard('عدد الموظفين', '0', '👔')
        self.cigarettes_card = StatCard('السجائر اليومية', '0', '🚬')
        
        stats_layout.addWidget(self.active_patients_card, 0, 0)
        stats_layout.addWidget(self.graduated_card, 0, 1)
        stats_layout.addWidget(self.revenue_card, 0, 2)
        stats_layout.addWidget(self.expenses_card, 1, 0)
        stats_layout.addWidget(self.profit_card, 1, 1)
        stats_layout.addWidget(self.employees_card, 1, 2)
        stats_layout.addWidget(self.cigarettes_card, 2, 0)
        
        layout.addLayout(stats_layout)
        
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('🔄 تحديث البيانات')
        refresh_btn.setFixedHeight(40)
        refresh_btn.clicked.connect(self.refresh_data)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        self.setLayout(layout)
        self.refresh_data()
    
    def refresh_data(self):
        active = self.patient_mgr.get_active_count()
        graduated = self.patient_mgr.get_graduated_count()
        revenue = self.payment_mgr.get_total_revenue()
        expenses = self.expense_mgr.get_total_expenses()
        profit = revenue - expenses
        employees = self.employee_mgr.get_active_count()
        cigarettes = self.patient_mgr.get_total_cigarettes()
        
        self.active_patients_card.update_value(str(active))
        self.graduated_card.update_value(str(graduated))
        self.revenue_card.update_value(f'{revenue:.2f} جنيه')
        self.expenses_card.update_value(f'{expenses:.2f} جنيه')
        self.profit_card.update_value(f'{profit:.2f} جنيه')
        self.employees_card.update_value(str(employees))
        self.cigarettes_card.update_value(str(cigarettes))
