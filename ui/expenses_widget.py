from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                             QLineEdit, QDateEdit, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

class AddExpenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('إضافة مصروف جديد')
        self.setFixedSize(450, 350)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText('بند المصروف')
        self.category_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('البند:'))
        layout.addWidget(self.category_input)
        
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
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText('وصف (اختياري)')
        self.description_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('الوصف:'))
        layout.addWidget(self.description_input)
        
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
            'category': self.category_input.text(),
            'amount': float(self.amount_input.text()) if self.amount_input.text() else 0,
            'expense_date': self.date_input.date().toString('yyyy-MM-dd'),
            'description': self.description_input.text()
        }

class ExpensesWidget(QWidget):
    def __init__(self, db, expense_mgr, current_user=None):  # --- NEW FEATURE: User Permissions ---
        super().__init__()
        self.db = db
        self.expense_mgr = expense_mgr
        self.current_user = current_user  # --- NEW FEATURE: User Permissions ---
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel('إدارة المصروفات')
        header.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        header.setStyleSheet('color: #1abc9c; padding: 20px;')
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignRight)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton('➕ إضافة مصروف جديد')
        add_btn.clicked.connect(self.add_expense)
        btn_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('🔄 تحديث')
        refresh_btn.clicked.connect(self.load_expenses)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'الرقم', 'البند', 'المبلغ', 'التاريخ', 'الوصف', 'إجراءات'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_expenses()
    
    def add_expense(self):
        dialog = AddExpenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['category'] and data['amount'] > 0:
                self.expense_mgr.add_expense(
                    data['category'], data['amount'],
                    data['expense_date'], data['description']
                )
                QMessageBox.information(self, 'نجح', 'تم إضافة المصروف بنجاح')
                self.load_expenses()
    
    def load_expenses(self):
        expenses = self.expense_mgr.get_all_expenses()
        self.table.setRowCount(len(expenses))
        
        for row, expense in enumerate(expenses):
            self.table.setItem(row, 0, QTableWidgetItem(str(expense[0])))
            self.table.setItem(row, 1, QTableWidgetItem(expense[1]))
            self.table.setItem(row, 2, QTableWidgetItem(f'{expense[2]:.2f}'))
            self.table.setItem(row, 3, QTableWidgetItem(expense[3]))
            self.table.setItem(row, 4, QTableWidgetItem(expense[4] if expense[4] else ''))
            
            if self.current_user and self.current_user.get('role') == 'admin':
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton('✏️')
                edit_btn.setFixedWidth(40)
                edit_btn.clicked.connect(lambda checked, eid=expense[0]: self.edit_expense(eid))
                actions_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton('🗑️')
                delete_btn.setFixedWidth(40)
                delete_btn.setStyleSheet('background-color: #e74c3c; color: white;')
                delete_btn.clicked.connect(lambda checked, eid=expense[0]: self.delete_expense(eid))
                actions_layout.addWidget(delete_btn)
                
                actions_widget.setLayout(actions_layout)
                self.table.setCellWidget(row, 5, actions_widget)
            else:
                no_access_label = QLabel('🔒')
                no_access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setCellWidget(row, 5, no_access_label)
    
    def edit_expense(self, expense_id):
        if not self.current_user or self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, 'تحذير', '⚠️ غير مصرح لك بتعديل البيانات')
            return
        
        expense = self.expense_mgr.get_expense(expense_id)
        if not expense:
            QMessageBox.warning(self, 'خطأ', 'لم يتم العثور على المصروف')
            return
        
        dialog = AddExpenseDialog(self)
        dialog.setWindowTitle('تعديل مصروف')
        dialog.category_input.setText(expense[1])
        dialog.amount_input.setText(str(expense[2]))
        dialog.date_input.setDate(QDate.fromString(expense[3], 'yyyy-MM-dd'))
        dialog.description_input.setText(expense[4] if expense[4] else '')
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['category'] and data['amount'] > 0:
                self.expense_mgr.update_expense(
                    expense_id, data['category'], data['amount'],
                    data['expense_date'], data['description']
                )
                QMessageBox.information(self, 'نجح', 'تم تعديل المصروف بنجاح')
                self.load_expenses()
    
    def delete_expense(self, expense_id):
        if not self.current_user or self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, 'تحذير', '⚠️ غير مصرح لك بحذف البيانات')
            return
        
        reply = QMessageBox.question(
            self, 'تأكيد الحذف',
            'هل أنت متأكد من حذف هذا المصروف؟\nلا يمكن التراجع عن هذا الإجراء.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.expense_mgr.delete_expense(expense_id)
            QMessageBox.information(self, 'نجح', 'تم حذف المصروف بنجاح')
            self.load_expenses()
