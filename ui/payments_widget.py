from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QDialog,
                             QLineEdit, QComboBox, QDateEdit, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

class AddPaymentDialog(QDialog):
    def __init__(self, patients, parent=None):
        super().__init__(parent)
        self.setWindowTitle('إضافة دفعة جديدة')
        self.setFixedSize(450, 350)
        self.patients = patients
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.patient_combo = QComboBox()
        for patient in self.patients:
            self.patient_combo.addItem(f'{patient[1]} - رقم {patient[0]}', patient[0])
        layout.addWidget(QLabel('المريض:'))
        layout.addWidget(self.patient_combo)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('المبلغ')
        self.amount_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('المبلغ:'))
        layout.addWidget(self.amount_input)
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        layout.addWidget(QLabel('تاريخ الدفعة:'))
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
            'patient_id': self.patient_combo.currentData(),
            'amount': float(self.amount_input.text()) if self.amount_input.text() else 0,
            'payment_date': self.date_input.date().toString('yyyy-MM-dd'),
            'notes': self.notes_input.text()
        }

class PaymentsWidget(QWidget):
    def __init__(self, db, payment_mgr, patient_mgr, current_user=None):  # --- NEW FEATURE: User Permissions ---
        super().__init__()
        self.db = db
        self.payment_mgr = payment_mgr
        self.patient_mgr = patient_mgr
        self.current_user = current_user  # --- NEW FEATURE: User Permissions ---
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel('إدارة المدفوعات')
        header.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        header.setStyleSheet('color: #1abc9c; padding: 20px;')
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignRight)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton('➕ إضافة دفعة جديدة')
        add_btn.clicked.connect(self.add_payment)
        btn_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton('🔄 تحديث')
        refresh_btn.clicked.connect(self.load_payments)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'الرقم', 'اسم المريض', 'المبلغ', 'التاريخ', 'ملاحظات', 'إجراءات'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_payments()
    
    def add_payment(self):
        patients = self.patient_mgr.get_all_patients('نشط')
        if not patients:
            QMessageBox.warning(self, 'تنبيه', 'لا يوجد مرضى نشطون')
            return
        
        dialog = AddPaymentDialog(patients, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['amount'] > 0:
                self.payment_mgr.add_payment(
                    data['patient_id'], data['amount'],
                    data['payment_date'], data['notes']
                )
                QMessageBox.information(self, 'نجح', 'تم إضافة الدفعة بنجاح')
                self.load_payments()
    
    def load_payments(self):
        payments = self.payment_mgr.get_all_payments()
        self.table.setRowCount(len(payments))
        
        for row, payment in enumerate(payments):
            self.table.setItem(row, 0, QTableWidgetItem(str(payment[0])))
            self.table.setItem(row, 1, QTableWidgetItem(payment[6]))
            self.table.setItem(row, 2, QTableWidgetItem(f'{payment[2]:.2f}'))
            self.table.setItem(row, 3, QTableWidgetItem(payment[3]))
            self.table.setItem(row, 4, QTableWidgetItem(payment[4] if payment[4] else ''))
            
            if self.current_user and self.current_user.get('role') == 'admin':
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton('✏️')
                edit_btn.setFixedWidth(40)
                edit_btn.clicked.connect(lambda checked, pid=payment[0]: self.edit_payment(pid))
                actions_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton('🗑️')
                delete_btn.setFixedWidth(40)
                delete_btn.setStyleSheet('background-color: #e74c3c; color: white;')
                delete_btn.clicked.connect(lambda checked, pid=payment[0]: self.delete_payment(pid))
                actions_layout.addWidget(delete_btn)
                
                actions_widget.setLayout(actions_layout)
                self.table.setCellWidget(row, 5, actions_widget)
            else:
                no_access_label = QLabel('🔒')
                no_access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setCellWidget(row, 5, no_access_label)
    
    def edit_payment(self, payment_id):
        if not self.current_user or self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, 'تحذير', '⚠️ غير مصرح لك بتعديل البيانات')
            return
        
        payment = self.payment_mgr.get_payment(payment_id)
        if not payment:
            QMessageBox.warning(self, 'خطأ', 'لم يتم العثور على الدفعة')
            return
        
        patients = self.patient_mgr.get_all_patients('نشط')
        all_patients = self.patient_mgr.get_all_patients()
        
        dialog = AddPaymentDialog(all_patients, self)
        dialog.setWindowTitle('تعديل دفعة')
        
        for i in range(dialog.patient_combo.count()):
            if dialog.patient_combo.itemData(i) == payment[1]:
                dialog.patient_combo.setCurrentIndex(i)
                break
        
        dialog.amount_input.setText(str(payment[2]))
        dialog.date_input.setDate(QDate.fromString(payment[3], 'yyyy-MM-dd'))
        dialog.notes_input.setText(payment[4] if payment[4] else '')
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['amount'] > 0:
                self.payment_mgr.update_payment(
                    payment_id, data['patient_id'], data['amount'],
                    data['payment_date'], data['notes']
                )
                QMessageBox.information(self, 'نجح', 'تم تعديل الدفعة بنجاح')
                self.load_payments()
    
    def delete_payment(self, payment_id):
        if not self.current_user or self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, 'تحذير', '⚠️ غير مصرح لك بحذف البيانات')
            return
        
        reply = QMessageBox.question(
            self, 'تأكيد الحذف',
            'هل أنت متأكد من حذف هذه الدفعة؟\nلا يمكن التراجع عن هذا الإجراء.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.payment_mgr.delete_payment(payment_id)
            QMessageBox.information(self, 'نجح', 'تم حذف الدفعة بنجاح')
            self.load_payments()
