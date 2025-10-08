from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class CalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_value = "0"
        self.previous_value = ""
        self.operation = ""
        self.new_number = True
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        title_layout = QHBoxLayout()
        title_label = QPushButton('🔢 آلة حاسبة')
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title_label.setStyleSheet('''
            QPushButton {
                background-color: #667eea;
                color: white;
                padding: 15px;
                border-radius: 8px;
                border: none;
            }
        ''')
        title_layout.addWidget(title_label)
        layout.addLayout(title_layout)
        
        self.display = QLineEdit()
        self.display.setText("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFont(QFont('Arial', 28, QFont.Weight.Bold))
        self.display.setStyleSheet('''
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #667eea;
                border-radius: 10px;
                padding: 20px;
                min-height: 60px;
            }
        ''')
        layout.addWidget(self.display)
        
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(8)
        
        buttons = [
            ['C', '⌫', '%', '/'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['±', '0', '.', '=']
        ]
        
        for row_idx, row in enumerate(buttons):
            for col_idx, button_text in enumerate(row):
                btn = QPushButton(button_text)
                btn.setFont(QFont('Arial', 16, QFont.Weight.Bold))
                btn.setMinimumHeight(60)
                
                if button_text in ['C', '⌫']:
                    btn.setStyleSheet('''
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border-radius: 8px;
                            border: none;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                        QPushButton:pressed {
                            background-color: #a93226;
                        }
                    ''')
                elif button_text in ['/', '×', '-', '+', '=']:
                    btn.setStyleSheet('''
                        QPushButton {
                            background-color: #667eea;
                            color: white;
                            border-radius: 8px;
                            border: none;
                        }
                        QPushButton:hover {
                            background-color: #5568d3;
                        }
                        QPushButton:pressed {
                            background-color: #4453c8;
                        }
                    ''')
                elif button_text in ['%', '±']:
                    btn.setStyleSheet('''
                        QPushButton {
                            background-color: #95a5a6;
                            color: white;
                            border-radius: 8px;
                            border: none;
                        }
                        QPushButton:hover {
                            background-color: #7f8c8d;
                        }
                        QPushButton:pressed {
                            background-color: #6c7a7b;
                        }
                    ''')
                else:
                    btn.setStyleSheet('''
                        QPushButton {
                            background-color: #34495e;
                            color: white;
                            border-radius: 8px;
                            border: none;
                        }
                        QPushButton:hover {
                            background-color: #2c3e50;
                        }
                        QPushButton:pressed {
                            background-color: #1a252f;
                        }
                    ''')
                
                btn.clicked.connect(lambda checked, text=button_text: self.button_clicked(text))
                buttons_layout.addWidget(btn, row_idx, col_idx)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def button_clicked(self, button_text):
        if button_text.isdigit():
            self.handle_digit(button_text)
        elif button_text == '.':
            self.handle_decimal()
        elif button_text in ['/', '×', '-', '+']:
            self.handle_operation(button_text)
        elif button_text == '=':
            self.handle_equals()
        elif button_text == 'C':
            self.handle_clear()
        elif button_text == '⌫':
            self.handle_backspace()
        elif button_text == '%':
            self.handle_percent()
        elif button_text == '±':
            self.handle_sign_change()
    
    def handle_digit(self, digit):
        if self.new_number:
            self.current_value = digit
            self.new_number = False
        else:
            if self.current_value == "0":
                self.current_value = digit
            else:
                self.current_value += digit
        self.update_display()
    
    def handle_decimal(self):
        if self.new_number:
            self.current_value = "0."
            self.new_number = False
        elif '.' not in self.current_value:
            self.current_value += '.'
        self.update_display()
    
    def handle_operation(self, op):
        if self.operation and not self.new_number:
            self.handle_equals()
        
        self.previous_value = self.current_value
        self.operation = op
        self.new_number = True
    
    def handle_equals(self):
        if not self.operation or not self.previous_value:
            return
        
        try:
            prev = float(self.previous_value)
            curr = float(self.current_value)
            
            if self.operation == '+':
                result = prev + curr
            elif self.operation == '-':
                result = prev - curr
            elif self.operation == '×':
                result = prev * curr
            elif self.operation == '/':
                if curr == 0:
                    self.current_value = "خطأ"
                    self.update_display()
                    self.reset()
                    return
                result = prev / curr
            
            if result == int(result):
                self.current_value = str(int(result))
            else:
                self.current_value = str(round(result, 8))
            
            self.update_display()
            self.previous_value = ""
            self.operation = ""
            self.new_number = True
            
        except Exception:
            self.current_value = "خطأ"
            self.update_display()
            self.reset()
    
    def handle_clear(self):
        self.current_value = "0"
        self.previous_value = ""
        self.operation = ""
        self.new_number = True
        self.update_display()
    
    def handle_backspace(self):
        if not self.new_number and len(self.current_value) > 1:
            self.current_value = self.current_value[:-1]
        else:
            self.current_value = "0"
            self.new_number = True
        self.update_display()
    
    def handle_percent(self):
        try:
            value = float(self.current_value)
            self.current_value = str(value / 100)
            self.update_display()
            self.new_number = True
        except Exception:
            pass
    
    def handle_sign_change(self):
        try:
            value = float(self.current_value)
            self.current_value = str(-value)
            self.update_display()
        except Exception:
            pass
    
    def reset(self):
        self.previous_value = ""
        self.operation = ""
        self.new_number = True
    
    def update_display(self):
        display_text = self.current_value
        
        if len(display_text) > 15:
            try:
                num = float(display_text)
                display_text = f"{num:.6e}"
            except:
                display_text = display_text[:15]
        
        self.display.setText(display_text)
